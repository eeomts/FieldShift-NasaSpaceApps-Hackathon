"""Cliente do OpenTopoData (SRTM 30 m): grade 3x3 em volta do ponto e declividade pelo método de Horn."""
import logging
import math
import time
from collections.abc import Callable
from dataclasses import dataclass

import httpx

log = logging.getLogger(__name__)

URL = "https://api.opentopodata.org/v1/srtm30m"
PASSO_M = 30.0  # distância entre os pontos da grade (resolução do SRTM 30 m)
M_POR_GRAU = 111_320.0  # metros por grau de latitude (e de longitude no equador)
TIMEOUT_S = 30.0
NOVAS_TENTATIVAS = 2
ESPERA_ENTRE_TENTATIVAS_S = (2.0, 6.0)
FONTE = "SRTM 30 m (OpenTopoData srtm30m), declividade pelo método de Horn em grade 3x3 de ~30 m"

# Classes de relevo da Embrapa (limites de declividade em %): (limite superior exclusivo, classe).
CLASSES = ((3.0, "plano"), (8.0, "suave_ondulado"), (20.0, "ondulado"), (45.0, "forte_ondulado"))
ULTIMA_CLASSE = "montanhoso"
LATITUDE_MAXIMA = 85.0  # SRTM cobre até ~60 N/S; acima disso o cos(lat) do passo em longitude explodiria


class ErroSrtm(Exception):
    """Falha ao obter a elevação do SRTM (o chamador usa a resposta do produtor, sem inventar)."""


@dataclass(frozen=True)
class Declividade:
    percentual: float
    classe: str
    fonte: str = FONTE


def classe_do_relevo(percentual: float) -> str:
    for limite, classe in CLASSES:
        if percentual < limite:
            return classe
    return ULTIMA_CLASSE


def pontos_da_grade(lat: float, lon: float) -> list[tuple[float, float]]:
    """Os 9 pontos (lat, lon), linhas do norte para o sul e colunas do oeste para o leste."""
    dlat = PASSO_M / M_POR_GRAU
    dlon = PASSO_M / (M_POR_GRAU * math.cos(math.radians(lat)))
    return [(lat + i * dlat, lon + j * dlon) for i in (1, 0, -1) for j in (-1, 0, 1)]


def declividade_horn(z: list[list[float]], passo_x_m: float = PASSO_M, passo_y_m: float = PASSO_M) -> float:
    """Declividade em % de uma grade 3x3 de elevações (m), linha 0 ao norte e coluna 0 a oeste."""
    dz_dx = ((z[0][2] + 2 * z[1][2] + z[2][2]) - (z[0][0] + 2 * z[1][0] + z[2][0])) / (8 * passo_x_m)
    dz_dy = ((z[0][0] + 2 * z[0][1] + z[0][2]) - (z[2][0] + 2 * z[2][1] + z[2][2])) / (8 * passo_y_m)
    return 100 * math.hypot(dz_dx, dz_dy)


class ClienteSrtm:
    def __init__(self, http: httpx.Client | None = None, espera: Callable[[float], None] = time.sleep):
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S))
        self.espera = espera

    def declividade(self, lat: float, lon: float) -> Declividade:
        if abs(lat) > LATITUDE_MAXIMA:
            raise ErroSrtm("Latitude fora da cobertura do SRTM.")
        pontos = pontos_da_grade(lat, lon)
        corpo = self._pedir({"locations": "|".join(f"{la:.6f},{lo:.6f}" for la, lo in pontos)})
        elevacoes = _interpretar(corpo, len(pontos))
        grade = [elevacoes[i : i + 3] for i in range(0, 9, 3)]
        # O passo em longitude (em metros) é o mesmo da latitude: os pontos já foram espaçados em metros.
        pct = declividade_horn(grade)
        return Declividade(percentual=round(pct, 2), classe=classe_do_relevo(pct))

    def _pedir(self, params: dict) -> dict:
        ultimo_erro = "sem resposta"
        for tentativa in range(NOVAS_TENTATIVAS + 1):
            if tentativa:
                self.espera(ESPERA_ENTRE_TENTATIVAS_S[min(tentativa - 1, len(ESPERA_ENTRE_TENTATIVAS_S) - 1)])
            try:
                r = self.http.get(URL, params=params)
            except httpx.TransportError as e:  # rede, DNS, timeout
                ultimo_erro = f"falha de rede ({type(e).__name__})"
                log.warning("SRTM: %s, tentativa %d", ultimo_erro, tentativa + 1)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                ultimo_erro = f"serviço indisponível (HTTP {r.status_code})"
                log.warning("SRTM: %s, tentativa %d", ultimo_erro, tentativa + 1)
                continue
            if r.status_code != 200:
                raise ErroSrtm(f"O OpenTopoData recusou o pedido (HTTP {r.status_code}).")
            try:
                return r.json()
            except ValueError as e:
                raise ErroSrtm("O OpenTopoData devolveu uma resposta que não é JSON.") from e
        raise ErroSrtm(f"Não consegui a elevação do SRTM agora: {ultimo_erro}.")


def _interpretar(corpo: dict, esperados: int) -> list[float]:
    """Elevações na ordem pedida. Qualquer ponto sem dado (oceano, vazio do SRTM) invalida a grade."""
    try:
        if corpo.get("status") != "OK":
            raise ErroSrtm("O OpenTopoData não respondeu com status OK.")
        elevacoes = [r["elevation"] for r in corpo["results"]]
    except (KeyError, TypeError, AttributeError) as e:
        raise ErroSrtm("Resposta do OpenTopoData em formato inesperado.") from e
    if len(elevacoes) != esperados:
        raise ErroSrtm("Resposta do OpenTopoData com número inesperado de pontos.")
    if any(e is None for e in elevacoes):
        raise ErroSrtm("O SRTM não tem elevação em algum ponto da grade (fora da cobertura).")
    return [float(e) for e in elevacoes]


def get_cliente() -> ClienteSrtm:
    return ClienteSrtm()
