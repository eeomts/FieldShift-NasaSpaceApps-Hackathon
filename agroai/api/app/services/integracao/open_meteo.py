"""Cliente da Open-Meteo: previsão diária de 7 dias para um ponto (D-014). Sem chave; dados CC BY 4.0."""
import logging
from dataclasses import dataclass
from datetime import date

import httpx

log = logging.getLogger(__name__)

URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_S = 20.0
VARIAVEIS = ("temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max", "weather_code")
UNIDADES = {"temperature_2m_max": "°C", "temperature_2m_min": "°C", "precipitation_sum": "mm", "precipitation_probability_max": "%"}


class ErroOpenMeteo(Exception):
    """Falha ao obter a previsão (o Dashboard diz que a previsão não veio, sem inventar)."""


@dataclass
class DiaPrevisao:
    data: date
    tmax: float | None  # °C
    tmin: float | None  # °C
    chuva_mm: float | None
    chance_chuva: int | None  # %
    codigo_tempo: int | None  # código WMO (0 céu limpo ... 95+ trovoada)


class ClienteOpenMeteo:
    def __init__(self, http: httpx.Client | None = None):
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S))

    def previsao(self, lat: float, lon: float, dias: int = 7) -> list[DiaPrevisao]:
        params = {"latitude": lat, "longitude": lon, "daily": ",".join(VARIAVEIS), "timezone": "auto", "forecast_days": dias}
        try:
            r = self.http.get(URL, params=params)
        except httpx.TransportError as e:
            raise ErroOpenMeteo(f"falha de rede ({type(e).__name__})") from e
        if r.status_code != 200:
            raise ErroOpenMeteo(f"HTTP {r.status_code}")
        try:
            corpo = r.json()
            diario, unidades = corpo["daily"], corpo.get("daily_units", {})
            for v, esperada in UNIDADES.items():
                if unidades.get(v) != esperada:
                    raise ErroOpenMeteo(f"unidade inesperada para {v}: {unidades.get(v)!r}")
            return [
                DiaPrevisao(
                    data=date.fromisoformat(d),
                    tmax=_num(diario["temperature_2m_max"][i]),
                    tmin=_num(diario["temperature_2m_min"][i]),
                    chuva_mm=_num(diario["precipitation_sum"][i]),
                    chance_chuva=None if (p := diario["precipitation_probability_max"][i]) is None else int(p),
                    codigo_tempo=None if (c := diario["weather_code"][i]) is None else int(c),
                )
                for i, d in enumerate(diario["time"])
            ]
        except (ValueError, KeyError, TypeError, IndexError) as e:
            raise ErroOpenMeteo("resposta em formato inesperado") from e


def _num(v) -> float | None:
    return None if v is None else round(float(v), 1)


def get_cliente() -> ClienteOpenMeteo:
    return ClienteOpenMeteo()
