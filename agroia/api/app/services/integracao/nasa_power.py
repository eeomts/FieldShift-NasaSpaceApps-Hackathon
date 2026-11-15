"""Cliente do NASA POWER (série diária de um ponto, comunidade AG). Valor -999 vira None."""
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

import httpx

log = logging.getLogger(__name__)

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETROS = ("T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M")
# Unidades que o cálculo supõe; se o POWER mudar, falha em vez de calcular errado.
UNIDADES = {
    "T2M": "C",
    "T2M_MAX": "C",
    "T2M_MIN": "C",
    "PRECTOTCORR": "mm/day",
    "RH2M": "%",
    "ALLSKY_SFC_SW_DWN": "MJ/m^2/day",
    "WS2M": "m/s",
}
TIMEOUT_S = 90.0
NOVAS_TENTATIVAS = 2
ESPERA_ENTRE_TENTATIVAS_S = (2.0, 6.0)


class ErroNasaPower(Exception):
    """Falha ao obter o clima do NASA POWER (o chamador diz ao produtor que não conseguiu, sem inventar)."""


@dataclass
class DiaPower:
    data: date
    t2m: float | None
    tmax: float | None
    tmin: float | None
    chuva: float | None
    ur: float | None
    radiacao: float | None
    vento: float | None


@dataclass
class SeriePower:
    lat: float
    lon: float
    elevacao_m: float | None
    dias: list[DiaPower]


class ClienteNasaPower:
    def __init__(self, http: httpx.Client | None = None, espera: Callable[[float], None] = time.sleep):
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S))
        self.espera = espera

    def serie_diaria(self, lat: float, lon: float, inicio: date, fim: date) -> SeriePower:
        params = {
            "parameters": ",".join(PARAMETROS),
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": inicio.strftime("%Y%m%d"),
            "end": fim.strftime("%Y%m%d"),
            "format": "JSON",
        }
        return _interpretar(self._pedir(params))

    def _pedir(self, params: dict) -> dict:
        ultimo_erro = "sem resposta"
        for tentativa in range(NOVAS_TENTATIVAS + 1):
            if tentativa:
                self.espera(ESPERA_ENTRE_TENTATIVAS_S[min(tentativa - 1, len(ESPERA_ENTRE_TENTATIVAS_S) - 1)])
            try:
                r = self.http.get(URL, params=params)
            except httpx.TransportError as e:  # rede, DNS, timeout
                ultimo_erro = f"falha de rede ({type(e).__name__})"
                log.warning("NASA POWER: %s, tentativa %d", ultimo_erro, tentativa + 1)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                ultimo_erro = f"serviço indisponível (HTTP {r.status_code})"
                log.warning("NASA POWER: %s, tentativa %d", ultimo_erro, tentativa + 1)
                continue
            if r.status_code != 200:
                raise ErroNasaPower(f"O NASA POWER recusou o pedido (HTTP {r.status_code}).")
            try:
                return r.json()
            except ValueError as e:
                raise ErroNasaPower("O NASA POWER devolveu uma resposta que não é JSON.") from e
        raise ErroNasaPower(f"Não consegui o clima do NASA POWER agora: {ultimo_erro}.")


def _interpretar(corpo: dict) -> SeriePower:
    try:
        series = corpo["properties"]["parameter"]
        unidades = corpo.get("parameters", {})
        fill = corpo.get("header", {}).get("fill_value", -999.0)
        lon, lat, *resto = corpo["geometry"]["coordinates"]
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise ErroNasaPower("Resposta do NASA POWER em formato inesperado.") from e

    faltando = [p for p in PARAMETROS if p not in series]
    if faltando:
        raise ErroNasaPower(f"Resposta do NASA POWER sem os parâmetros: {', '.join(faltando)}.")
    for p, esperada in UNIDADES.items():
        encontrada = unidades.get(p, {}).get("units")
        if encontrada != esperada:
            raise ErroNasaPower(f"Unidade inesperada no NASA POWER para {p}: {encontrada!r}.")

    def valor(p: str, chave: str) -> float | None:
        v = series[p].get(chave)
        return None if v is None or v == fill else float(v)

    datas = sorted(set().union(*(series[p].keys() for p in PARAMETROS)))
    try:
        dias = [
            DiaPower(
                data=datetime.strptime(k, "%Y%m%d").date(),
                t2m=valor("T2M", k),
                tmax=valor("T2M_MAX", k),
                tmin=valor("T2M_MIN", k),
                chuva=valor("PRECTOTCORR", k),
                ur=valor("RH2M", k),
                radiacao=valor("ALLSKY_SFC_SW_DWN", k),
                vento=valor("WS2M", k),
            )
            for k in datas
        ]
    except ValueError as e:
        raise ErroNasaPower("Resposta do NASA POWER com data em formato inesperado.") from e
    elevacao = resto[0] if resto and resto[0] is not None and resto[0] != fill else None
    return SeriePower(lat=float(lat), lon=float(lon), elevacao_m=None if elevacao is None else float(elevacao), dias=dias)


def get_cliente() -> ClienteNasaPower:
    return ClienteNasaPower()
