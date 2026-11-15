"""Solo de um ponto: SoilGrids com cache por propriedade (retoma de onde parou), "sem dado" guardado e os derivados."""
import logging

from fastapi import Depends

from app.core.erros import ErroDeNegocio
from app.repositories.solo_repository import SoloRepository
from app.schemas.solo import SoloPonto
from app.services.integracao.soilgrids import (
    FONTE,
    PROPRIEDADES,
    CamadaSolo,
    ClienteSoilGrids,
    ErroSoilGrids,
    get_cliente,
    montar_amostra,
)
from app.services.solo import derivados

log = logging.getLogger(__name__)

CASAS_DECIMAIS = 2
MAX_FALHAS_POR_BUSCA = 2  # com o serviço fora do ar, desiste da busca (o que veio fica guardado)
# Propriedade do SoilGrids -> campo do SoloPonto (também é a chave de `incerteza`).
CAMPOS = {
    "clay": "argila_pct", "sand": "areia_pct", "silt": "silte_pct", "soc": "carbono_g_kg",
    "phh2o": "ph", "cec": "ctc_cmol_kg", "bdod": "densidade_g_cm3",
}  # fmt: skip


def chave_do_ponto(lat: float, lon: float) -> str:
    """Ponto arredondado a 3 casas (~110 m): o pixel do mapa tem 250 m, então vizinhos dividem a mesma linha."""
    return f"{lat:.3f}_{lon:.3f}"


def _r(v: float | None) -> float | None:
    return None if v is None else round(v, CASAS_DECIMAIS)


def utilizavel(p: SoloPonto) -> bool:
    """O retrato só é "pronto" com a textura (argila, areia e silte) ou com o ponto sem dado no mapa."""
    return p.sem_dado or None not in (p.argila_pct, p.areia_pct, p.silte_pct)


def ponto_da_camada(c: CamadaSolo) -> SoloPonto:
    """Números da camada + derivados (classe textural, matéria orgânica, K). O que não veio fica None."""
    v = {campo: _r(c.valores.get(prop)) for prop, campo in CAMPOS.items()}
    mo = derivados.materia_organica_g_kg(v["carbono_g_kg"])
    return SoloPonto(
        **v,
        materia_organica_g_kg=_r(mo),
        classe_textural=derivados.classe_textural(v["argila_pct"], v["areia_pct"], v["silte_pct"]),
        k_usle=derivados.erodibilidade_k(v["argila_pct"], v["areia_pct"], v["silte_pct"], v["carbono_g_kg"]),
        incerteza={campo: _r(c.incerteza.get(prop)) for prop, campo in CAMPOS.items()},
    )


class SoloService:
    def __init__(self, repositorio: SoloRepository = Depends(), cliente: ClienteSoilGrids = Depends(get_cliente)):
        self.repositorio = repositorio
        self.cliente = cliente

    def obter(self, lat: float, lon: float) -> SoloPonto | None:
        """Solo de 0 a 30 cm no ponto. Pede ao SoilGrids só as propriedades que o cache ainda não tem e grava cada uma na hora.

        Resultado parcial vale: o que faltou fica None. Área urbana ou água: ponto com sem_dado. Nada obtido (nem no cache): None.
        """
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ErroDeNegocio(422, "Latitude deve estar entre -90 e 90 e longitude entre -180 e 180.")
        chave = chave_do_ponto(lat, lon)
        propriedades = self.repositorio.por_chave(chave)
        faltam = [p for p in PROPRIEDADES if p not in propriedades]
        if faltam and not any(p.sem_dado for p in propriedades.values()):
            self.repositorio.liberar_conexao()
            falhas = 0
            for nome in faltam:  # textura primeiro (clay, sand, silt), depois soc, phh2o, bdod, cec
                try:
                    nova = self.cliente.propriedade(lat, lon, nome)
                except ErroSoilGrids as e:
                    log.warning("SoilGrids falhou em %s: %s", nome, e)
                    falhas += 1
                    if falhas >= MAX_FALHAS_POR_BUSCA:
                        break
                    continue
                self.repositorio.gravar(chave, nova)
                propriedades[nome] = nova
                if nova.sem_dado:
                    break
        if not propriedades:
            return None
        amostra = montar_amostra(propriedades)
        return SoloPonto(fonte=FONTE, sem_dado=True) if amostra.sem_dado else ponto_da_camada(amostra.superficial)
