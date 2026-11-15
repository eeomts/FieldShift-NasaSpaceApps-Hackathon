"""Célula da grade MERRA-2 do NASA POWER: o centro de um ponto e o id usado como chave do cache."""
import math

PASSO_LAT = 0.5
PASSO_LON = 0.625


def centro_da_celula(lat: float, lon: float) -> tuple[float, float]:
    """Centro da célula (0,5° x 0,625°) que contém o ponto. Meio exato vai para o lado de cima (sem arredondar par)."""
    clon = math.floor(lon / PASSO_LON + 0.5) * PASSO_LON
    if clon >= 180:  # a célula centrada em 180° é a mesma de -180° (a grade dá a volta)
        clon -= 360
    return math.floor(lat / PASSO_LAT + 0.5) * PASSO_LAT, clon


def id_da_celula(lat: float, lon: float) -> str:
    """Id no formato "<lat>_<lon>" do centro, ex. "-17.5_-51.25"."""
    clat, clon = centro_da_celula(lat, lon)
    return f"{clat}_{clon}"
