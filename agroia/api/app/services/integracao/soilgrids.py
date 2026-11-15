"""Cliente do SoilGrids 2.0 (ISRIC): uma propriedade do solo por pedido, em duas camadas (0–30 e 0–100 cm), já em unidades usuais."""
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import httpx

log = logging.getLogger(__name__)

URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
FONTE = "SoilGrids 2.0 (ISRIC), 250 m"
# A API pública é lenta e tem limite de poucas chamadas por minuto. Medido em 15/11: o custo é por PROPRIEDADE
# (1 propriedade × 5 profundidades × 4 estatísticas levou de 20 a 90 s; 3 propriedades passaram de 180 s e o gateway
# devolveu 504). Por isso o pedido sai com uma propriedade por vez, e só as 7 que o app usa.
TIMEOUT_S = 170.0  # o gateway do ISRIC devolve 504 aos 180 s: esperar quase isso
NOVAS_TENTATIVAS = 1
ESPERA_ENTRE_TENTATIVAS_S = 20.0
INTERVALO_MINIMO_ENTRE_PEDIDOS_S = 15.0  # entre o início de um pedido e o do próximo (limite de uso justo)

# Nitrogênio e pedregosidade (cfvo) ficam fora por ora: nada no app os usa e cada propriedade custa um pedido lento.
PROPRIEDADES = ("clay", "sand", "silt", "soc", "phh2o", "bdod", "cec")
PROFUNDIDADES = ("0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm")
ESTATISTICAS = ("mean", "Q0.05", "Q0.5", "Q0.95")
# Espessura (cm) de cada profundidade: peso da média ponderada.
ESPESSURA_CM = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15, "30-60cm": 30, "60-100cm": 40}
CAMADAS = {
    "superficial": ("0-5cm", "5-15cm", "15-30cm"),
    "raizes": PROFUNDIDADES,
}
# Unidade mapeada ÷ fator = unidade usual (tabela de SOILGRIDS em "Tratamento de dados e arquitetura da base única").
FATORES = {"clay": 10, "sand": 10, "silt": 10, "soc": 10, "phh2o": 10, "bdod": 100, "cec": 10, "nitrogen": 100, "cfvo": 10}
TEXTURA = ("clay", "sand", "silt")  # %
SOMA_TEXTURA = 100.0
TOLERANCIA_SOMA = 2.0


class ErroSoilGrids(Exception):
    """Falha ao obter o solo do SoilGrids (o retrato segue só com o que o produtor contou)."""


@dataclass
class CamadaSolo:
    """Médias ponderadas de uma camada. Chave = propriedade do SoilGrids; sem valor = None."""

    valores: dict[str, float | None] = field(default_factory=dict)
    incerteza: dict[str, float | None] = field(default_factory=dict)  # (Q0,95 − Q0,05) ÷ Q0,50


@dataclass
class PropriedadeSolo:
    """Uma propriedade do SoilGrids num ponto, já convertida: média de 0–30 e de 0–100 cm e a incerteza relativa de cada."""

    nome: str
    superficial: float | None = None
    raizes: float | None = None
    incerteza_superficial: float | None = None
    incerteza_raizes: float | None = None
    sem_dado: bool = False  # área urbana ou água: o mapa devolve tudo nulo


@dataclass
class AmostraSoilGrids:
    superficial: CamadaSolo | None  # 0–30 cm
    raizes: CamadaSolo | None  # 0–100 cm
    sem_dado: bool = False  # área urbana ou água: o mapa devolve tudo nulo


def converter(propriedade: str, bruto: float | int | None) -> float | None:
    """Unidade mapeada → unidade usual; nulo continua nulo (nunca vira 0)."""
    return None if bruto is None else bruto / FATORES[propriedade]


def media_ponderada(valores: dict[str, float | None]) -> float | None:
    """Média pela espessura das profundidades que têm valor; sem nenhuma, None."""
    pares = [(v, ESPESSURA_CM[p]) for p, v in valores.items() if v is not None and p in ESPESSURA_CM]
    total = sum(e for _, e in pares)
    return None if total == 0 else sum(v * e for v, e in pares) / total


def incerteza_relativa(q05: float | None, q50: float | None, q95: float | None) -> float | None:
    if q05 is None or q50 is None or q95 is None or q50 <= 0:
        return None
    return (q95 - q05) / q50


def renormalizar_textura(valores: dict[str, float | None]) -> dict[str, float | None]:
    """Argila + areia + silte deve dar 100 % (± 2); fora disso, reescala as três para somar 100."""
    partes = [valores.get(p) for p in TEXTURA]
    if any(v is None for v in partes):
        return valores
    soma = sum(partes)
    if soma <= 0 or abs(soma - SOMA_TEXTURA) <= TOLERANCIA_SOMA:
        return valores
    return {**valores, **{p: v * SOMA_TEXTURA / soma for p, v in zip(TEXTURA, partes)}}


def _niveis(corpo: dict, nome: str) -> dict[str, dict[str, float | None]]:
    """`[estatistica][profundidade]` já convertido, da camada `nome` da resposta."""
    try:
        camada = next(c for c in corpo["properties"]["layers"] if c["name"] == nome)
        niveis: dict[str, dict[str, float | None]] = {e: {} for e in ESTATISTICAS}
        for d in camada["depths"]:
            for estatistica in ESTATISTICAS:
                niveis[estatistica][d["label"]] = converter(nome, (d.get("values") or {}).get(estatistica))
    except (KeyError, TypeError, AttributeError, StopIteration) as e:
        raise ErroSoilGrids("Resposta do SoilGrids em formato inesperado.") from e
    return niveis


def interpretar_propriedade(corpo: dict, nome: str) -> PropriedadeSolo:
    """Uma propriedade da resposta → médias ponderadas (0–30 e 0–100 cm) e incertezas. Tudo nulo = sem dado."""
    niveis = _niveis(corpo, nome)
    if all(v is None for v in niveis["mean"].values()):
        return PropriedadeSolo(nome, sem_dado=True)

    def media(estatistica: str, profundidades: tuple[str, ...]) -> float | None:
        return media_ponderada({p: niveis[estatistica].get(p) for p in profundidades})

    def incerteza(profundidades: tuple[str, ...]) -> float | None:
        return incerteza_relativa(media("Q0.05", profundidades), media("Q0.5", profundidades), media("Q0.95", profundidades))

    sup, rai = CAMADAS["superficial"], CAMADAS["raizes"]
    return PropriedadeSolo(nome, media("mean", sup), media("mean", rai), incerteza(sup), incerteza(rai))


def montar_amostra(propriedades: dict[str, PropriedadeSolo]) -> AmostraSoilGrids:
    """Junta as propriedades que já vieram (pode faltar alguma: fica sem a chave). Qualquer uma sem dado = ponto sem dado."""
    if any(p.sem_dado for p in propriedades.values()):
        return AmostraSoilGrids(None, None, sem_dado=True)
    camadas = []
    for atributo in ("superficial", "raizes"):
        valores = {n: getattr(p, atributo) for n, p in propriedades.items()}
        incerteza = {n: getattr(p, f"incerteza_{atributo}") for n, p in propriedades.items()}
        camadas.append(CamadaSolo(renormalizar_textura(valores), incerteza))
    return AmostraSoilGrids(*camadas)


def interpretar(corpo: dict) -> AmostraSoilGrids:
    """Resposta com várias propriedades (ou uma) → amostra."""
    try:
        nomes = [c["name"] for c in corpo["properties"]["layers"] if c["name"] in FATORES]
    except (KeyError, TypeError) as e:
        raise ErroSoilGrids("Resposta do SoilGrids em formato inesperado.") from e
    if not nomes:
        raise ErroSoilGrids("Resposta do SoilGrids sem propriedades.")
    return montar_amostra({n: interpretar_propriedade(corpo, n) for n in nomes})


class ClienteSoilGrids:
    def __init__(
        self,
        http: httpx.Client | None = None,
        espera: Callable[[float], None] = time.sleep,
        relogio: Callable[[], float] = time.monotonic,
    ):
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S, connect=15.0))
        self.espera = espera
        self.relogio = relogio
        self._ultimo_pedido: float | None = None

    def propriedade(self, lat: float, lon: float, nome: str) -> PropriedadeSolo:
        """Um pedido (uma propriedade, as 5 profundidades e as 4 estatísticas)."""
        params = [("lat", f"{lat:.6f}"), ("lon", f"{lon:.6f}"), ("property", nome)]
        params += [("depth", d) for d in PROFUNDIDADES]
        params += [("value", e) for e in ESTATISTICAS]
        return interpretar_propriedade(self._pedir(params), nome)

    def _respeitar_o_limite(self) -> None:
        agora = self.relogio()
        if self._ultimo_pedido is not None:
            falta = INTERVALO_MINIMO_ENTRE_PEDIDOS_S - (agora - self._ultimo_pedido)
            if falta > 0:
                self.espera(falta)
        self._ultimo_pedido = self.relogio()

    def _pedir(self, params: list[tuple[str, str]]) -> dict:
        ultimo_erro = "sem resposta"
        for tentativa in range(NOVAS_TENTATIVAS + 1):
            if tentativa:
                self.espera(ESPERA_ENTRE_TENTATIVAS_S)
            self._respeitar_o_limite()
            try:
                r = self.http.get(URL, params=params)
            except httpx.TransportError as e:  # rede, DNS, timeout
                ultimo_erro = f"falha de rede ({type(e).__name__})"
                log.warning("SoilGrids: %s, tentativa %d", ultimo_erro, tentativa + 1)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                ultimo_erro = f"serviço indisponível (HTTP {r.status_code})"
                log.warning("SoilGrids: %s, tentativa %d", ultimo_erro, tentativa + 1)
                continue
            if r.status_code != 200:
                raise ErroSoilGrids(f"O SoilGrids recusou o pedido (HTTP {r.status_code}).")
            try:
                return r.json()
            except ValueError as e:
                raise ErroSoilGrids("O SoilGrids devolveu uma resposta que não é JSON.") from e
        raise ErroSoilGrids(f"Não consegui o solo do SoilGrids agora: {ultimo_erro}.")


def get_cliente() -> ClienteSoilGrids:
    return ClienteSoilGrids()
