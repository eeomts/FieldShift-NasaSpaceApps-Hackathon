"""País e município/condado de um ponto (ponto-em-polígono nas malhas do IBGE e do Census)."""
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from shapely import STRtree
from shapely.geometry import Point, shape

from app.core.caminhos import RAIZ_REPO

MALHAS = (  # (país, arquivo, propriedade com o código)
    ("BR", RAIZ_REPO / "data" / "brasil" / "municipios" / "municipios.geojson", "municipio_id"),  # IBGE, 7 dígitos
    ("US", RAIZ_REPO / "data" / "eua" / "condados" / "condados.geojson", "condado_id"),  # FIPS, 5 dígitos
)


@dataclass(frozen=True)
class Malha:
    pais: str
    arvore: STRtree
    codigos: tuple[str, ...]  # na mesma ordem das geometrias da árvore


def carregar_malha(pais: str, caminho: Path, propriedade: str) -> Malha:
    features = json.loads(caminho.read_text(encoding="utf-8"))["features"]
    geometrias = [shape(f["geometry"]) for f in features]
    return Malha(pais, STRtree(geometrias), tuple(str(f["properties"][propriedade]) for f in features))


@lru_cache
def _malhas() -> tuple[Malha, ...]:
    return tuple(carregar_malha(*m) for m in MALHAS)


def pais_e_codigo(lat: float, lon: float) -> tuple[str | None, str | None]:
    """("BR", "<IBGE 7>"), ("US", "<FIPS 5>") ou (None, None) fora das duas malhas. Ponto na divisa: o menor código."""
    ponto = Point(lon, lat)
    for malha in _malhas():
        achados = malha.arvore.query(ponto, predicate="intersects")
        if len(achados):
            return malha.pais, min(malha.codigos[i] for i in achados)
    return None, None
