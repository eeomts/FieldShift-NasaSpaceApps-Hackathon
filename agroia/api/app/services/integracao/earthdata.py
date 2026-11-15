"""Cliente do Earthdata: acha os arquivos no CMR e lê só os pixels do ponto pelo OPeNDAP (sem baixar o arquivo).

O token (EARTHDATA_TOKEN) vem do ambiente e vai só no cabeçalho Authorization; nunca aparece em log nem em URL.
"""
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import quote

import httpx

from app.core.config import get_settings

log = logging.getLogger(__name__)

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
OPENDAP = "https://opendap.earthdata.nasa.gov/"
TIMEOUT_S = 60.0
NOVAS_TENTATIVAS = 1

_ERRO_DAP = re.compile(r"Error\s*\{\s*code\s*=\s*(\d+)")


class ErroEarthdata(Exception):
    """Falha ao ler um produto da NASA. `sem_permissao` indica token ausente, vencido ou sem acesso ao arquivo."""

    def __init__(self, mensagem: str, sem_permissao: bool = False):
        super().__init__(mensagem)
        self.sem_permissao = sem_permissao


@dataclass(frozen=True)
class Granulo:
    titulo: str
    data: date
    opendap: str  # URL do granulo no OPeNDAP (sem sufixo)


class ClienteEarthdata:
    def __init__(self, token: str | None = None, http: httpx.Client | None = None):
        self.token = token
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S), follow_redirects=True)

    @property
    def tem_token(self) -> bool:
        return bool(self.token)

    # --- CMR (catálogo, público) -------------------------------------------------
    def granulos(
        self,
        nome: str,
        inicio: date,
        fim: date,
        versao: str | None = None,
        ponto: tuple[float, float] | None = None,
        limite: int = 50,
        mais_recentes_primeiro: bool = True,
    ) -> list[Granulo]:
        params: dict = {
            "short_name": nome,
            "temporal": f"{inicio.isoformat()}T00:00:00Z,{fim.isoformat()}T23:59:59Z",
            "page_size": limite,
            "sort_key": "-start_date" if mais_recentes_primeiro else "start_date",
        }
        if versao:
            params["version"] = versao
        if ponto:
            lat, lon = ponto
            params["point"] = f"{lon},{lat}"
        r = self._get(CMR, params=params, autenticar=False)
        try:
            entradas = r.json()["feed"]["entry"]
        except (ValueError, KeyError, TypeError) as e:
            raise ErroEarthdata("O catálogo da NASA (CMR) respondeu num formato inesperado.") from e
        saida = []
        for e in entradas:
            url = next((l["href"] for l in e.get("links", []) if l.get("href", "").startswith(OPENDAP)), None)
            if not url:
                continue
            try:
                d = datetime.fromisoformat(e["time_start"].replace("Z", "+00:00")).date()
            except (KeyError, ValueError):
                continue
            saida.append(Granulo(titulo=e.get("title", ""), data=d, opendap=url))
        return saida

    # --- OPeNDAP (dados, exige token) ---------------------------------------------
    def recorte(self, granulo_url: str, variaveis: dict[str, str]) -> dict[str, list[list[float | None]]]:
        """Lê recortes pequenos. `variaveis` = {caminho: índices DAP4}, ex.: {"/sm_surface": "[10:12][20:22]"}.

        Devolve {caminho: linhas de valores}. Valores de preenchimento (<= -9990) viram None.
        """
        if not self.tem_token:
            raise ErroEarthdata("Falta o EARTHDATA_TOKEN no ambiente.", sem_permissao=True)
        ce = ";".join(f"{v}{idx}" for v, idx in variaveis.items())
        url = f"{granulo_url}.dap.csv?dap4.ce={quote(ce, safe='/;:_')}"
        texto = self._get(url, autenticar=True).text
        m = _ERRO_DAP.search(texto)
        if m:
            codigo = int(m.group(1))
            raise ErroEarthdata(
                f"O OPeNDAP da NASA recusou a leitura (código {codigo}).", sem_permissao=codigo in (401, 403)
            )
        return interpretar_csv_dap(texto, list(variaveis))

    def _get(self, url: str, params: dict | None = None, autenticar: bool = True) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self.token}"} if autenticar and self.token else {}
        ultimo = "sem resposta"
        for tentativa in range(NOVAS_TENTATIVAS + 1):
            try:
                r = self.http.get(url, params=params, headers=headers)
            except httpx.TransportError as e:
                ultimo = f"falha de rede ({type(e).__name__})"
                log.warning("Earthdata: %s, tentativa %d", ultimo, tentativa + 1)
                continue
            if r.status_code in (401, 403):
                raise ErroEarthdata(f"A NASA recusou o acesso (HTTP {r.status_code}).", sem_permissao=True)
            if r.status_code == 429 or r.status_code >= 500:
                ultimo = f"serviço indisponível (HTTP {r.status_code})"
                log.warning("Earthdata: %s, tentativa %d", ultimo, tentativa + 1)
                continue
            if r.status_code != 200:
                raise ErroEarthdata(f"A NASA recusou o pedido (HTTP {r.status_code}).")
            return r
        raise ErroEarthdata(f"Não consegui falar com a NASA agora: {ultimo}.")


def _numero(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return None if v != v or v <= -9990 else v  # NaN ou preenchimento


def interpretar_csv_dap(texto: str, variaveis: list[str]) -> dict[str, list[list[float | None]]]:
    """Linhas do tipo `/caminho/var[0], 1.0, 2.0` viram {"/caminho/var": [[1.0, 2.0], ...]}, na ordem."""
    saida: dict[str, list[list[float | None]]] = {v: [] for v in variaveis}
    for linha in texto.splitlines():
        if not linha.startswith("/") or "," not in linha:
            continue
        chave, _, resto = linha.partition(",")
        nome = chave.split("[", 1)[0].strip()
        if nome in saida:
            saida[nome].append([_numero(x) for x in resto.split(",")])
    faltando = [v for v, linhas in saida.items() if not linhas]
    if faltando:
        raise ErroEarthdata(f"Resposta do OPeNDAP sem a variável {', '.join(faltando)}.")
    return saida


def get_cliente() -> ClienteEarthdata:
    return ClienteEarthdata(token=get_settings().earthdata_token)
