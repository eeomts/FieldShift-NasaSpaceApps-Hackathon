"""Cliente da climatologia mensal do NASA POWER (temperatura e chuva médias de cada mês). -999 vira None."""
import logging
from dataclasses import dataclass

import httpx

from app.services.integracao.cache import CacheLru

log = logging.getLogger(__name__)

URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
TIMEOUT_S = 20.0
_MESES = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
_cache = CacheLru()


class ErroPowerClimatologia(Exception):
    """O POWER não respondeu ou devolveu algo inesperado."""


@dataclass
class ClimatologiaMensal:
    temp_c: list[float | None]  # T2M, média de cada mês (jan..dez)
    chuva_mm_dia: list[float | None]  # PRECTOTCORR em mm/dia (jan..dez)


class ClientePowerClimatologia:
    def __init__(self, http: httpx.Client | None = None):
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S))

    def mensal(self, lat: float, lon: float) -> ClimatologiaMensal:
        """Climatologia do ponto. Lança ErroPowerClimatologia se falhar."""
        if (guardado := _cache.pegar((lat, lon))) is not None:
            return guardado
        params = {"parameters": "T2M,PRECTOTCORR", "community": "AG", "latitude": lat, "longitude": lon, "format": "JSON"}
        try:
            r = self.http.get(URL, params=params)
            r.raise_for_status()
            corpo = r.json()
            serie = corpo["properties"]["parameter"]
            fill = corpo.get("header", {}).get("fill_value", -999.0)
            unidades = {p: corpo["parameters"][p]["units"] for p in ("T2M", "PRECTOTCORR")}
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as e:
            raise ErroPowerClimatologia(type(e).__name__) from e
        if unidades != {"T2M": "C", "PRECTOTCORR": "mm/day"}:  # se mudar, falha em vez de calcular errado
            raise ErroPowerClimatologia(f"unidades inesperadas: {unidades}")

        def mensal(parametro: str) -> list[float | None]:
            valores = [serie[parametro].get(m) for m in _MESES]
            return [None if v is None or v == fill else float(v) for v in valores]

        try:
            resultado = ClimatologiaMensal(temp_c=mensal("T2M"), chuva_mm_dia=mensal("PRECTOTCORR"))
        except (KeyError, TypeError, ValueError) as e:
            raise ErroPowerClimatologia(type(e).__name__) from e
        _cache.guardar((lat, lon), resultado)
        return resultado


def get_power_climatologia() -> ClientePowerClimatologia:
    return ClientePowerClimatologia()
