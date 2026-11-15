"""Em que pixel de cada produto da NASA cai um ponto (lat, lon). Só matemática, sem rede.

- MODIS (MOD13Q1): projeção senoidal, tiles hXXvYY de 4800 x 4800 pixels de ~231,66 m.
- SMAP L4 (SPL4SMGP): EASE-Grid 2.0 global de 9 km (EPSG:6933), 1624 linhas x 3856 colunas.
- GPM IMERG: grade regular de 0,1°, centros de -179,95 a 179,95 (lon) e de -89,95 a 89,95 (lat).
"""
import math
from dataclasses import dataclass

# MODIS senoidal (MODIS Land Grid, esfera de raio 6 371 007,181 m)
_R_MODIS = 6_371_007.181
_TILE_M = 1_111_950.5197665
_X_MIN = -20_015_109.354
_Y_MAX = 10_007_554.677
PIXELS_TILE_250M = 4800

# EASE-Grid 2.0 global, 9 km (elipsoide WGS84, paralelo padrão 30°)
_A = 6_378_137.0
_E2 = 0.0066943799901413165
_E = math.sqrt(_E2)
_K0 = math.cos(math.radians(30.0)) / math.sqrt(1 - _E2 * math.sin(math.radians(30.0)) ** 2)
_CELULA_EASE_M = 9008.055210146
_X0_EASE = -17_367_530.44516138
_Y0_EASE = 7_314_540.83113623
LINHAS_EASE, COLUNAS_EASE = 1624, 3856

# IMERG
COLUNAS_IMERG, LINHAS_IMERG = 3600, 1800


@dataclass(frozen=True)
class PixelModis:
    h: int
    v: int
    linha: int
    coluna: int

    @property
    def tile(self) -> str:
        return f"h{self.h:02d}v{self.v:02d}"


def pixel_modis(lat: float, lon: float) -> PixelModis:
    x = _R_MODIS * math.radians(lon) * math.cos(math.radians(lat))
    y = _R_MODIS * math.radians(lat)
    dx, dy = x - _X_MIN, _Y_MAX - y
    h, v = int(dx // _TILE_M), int(dy // _TILE_M)
    tamanho = _TILE_M / PIXELS_TILE_250M
    linha = min(int((dy - v * _TILE_M) // tamanho), PIXELS_TILE_250M - 1)
    coluna = min(int((dx - h * _TILE_M) // tamanho), PIXELS_TILE_250M - 1)
    return PixelModis(h=h, v=v, linha=linha, coluna=coluna)


def _q(phi: float) -> float:
    s = math.sin(phi)
    return (1 - _E2) * (s / (1 - _E2 * s * s) - (1 / (2 * _E)) * math.log((1 - _E * s) / (1 + _E * s)))


def celula_ease2_9km(lat: float, lon: float) -> tuple[int, int]:
    """(linha, coluna) da célula do SMAP L4 que contém o ponto."""
    x = _A * _K0 * math.radians(lon)
    y = _A * _q(math.radians(lat)) / (2 * _K0)
    linha = int((_Y0_EASE - y) // _CELULA_EASE_M)
    coluna = int((x - _X0_EASE) // _CELULA_EASE_M)
    return min(max(linha, 0), LINHAS_EASE - 1), min(max(coluna, 0), COLUNAS_EASE - 1)


def celula_imerg(lat: float, lon: float) -> tuple[int, int]:
    """(índice de lon, índice de lat) da célula de 0,1° do IMERG; a variável é precipitation[time][lon][lat]."""
    i_lon = min(max(math.floor((lon + 180) * 10), 0), COLUNAS_IMERG - 1)  # célula i vai de -180+0,1i a -180+0,1(i+1)
    i_lat = min(max(math.floor((lat + 90) * 10), 0), LINHAS_IMERG - 1)
    return i_lon, i_lat


def janela(centro: int, tamanho_total: int, raio: int = 1) -> tuple[int, int, int]:
    """Faixa [ini, fim] de até 2*raio+1 índices em volta do centro, sem sair da grade, e a posição do centro nela."""
    ini = max(centro - raio, 0)
    fim = min(centro + raio, tamanho_total - 1)
    return ini, fim, centro - ini
