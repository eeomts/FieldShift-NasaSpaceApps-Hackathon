"""Registro das fontes de dados que o app usa de fato; atualizar a cada integração nova."""
from dataclasses import dataclass


@dataclass(frozen=True)
class FonteStatus:
    nome: str
    para_que: str
    usada: bool


FONTES: list[FonteStatus] = [
    FonteStatus(
        "NASA POWER",
        "clima mensal da célula de ~50 km desde 1991: chuva, temperatura, geada, calor, chuva forte e sequência seca; "
        "a evapotranspiração (ET0) é calculada pelo AgroIA com o método FAO-56",
        True,
    ),
    FonteStatus("base de culturas do AgroIA", "parâmetros de 17 culturas no Brasil, com fontes", True),
    FonteStatus("textos da base de conhecimento do AgroIA", "explicações de conceitos", True),
    FonteStatus("respostas do produtor no cadastro da fazenda", "ficha da fazenda", True),
    FonteStatus("GPM IMERG", "chuva de satélite de ~10 km", False),
    FonteStatus("SoilGrids", "solo por ponto", False),
    FonteStatus("SMAP", "umidade do solo", False),
    FonteStatus("MODIS/VIIRS", "NDVI, o verde da lavoura", False),
    FonteStatus("IBGE PAM", "produção agrícola por município", False),
    FonteStatus("ZARC", "janelas de plantio", False),
    FonteStatus("USDA NASS", "produção nos EUA", False),
    FonteStatus("SRTM", "relevo; o motor de rotação já usa, mas o chat ainda não mostra", False),
]


def _lista(usada: bool) -> str:
    return "; ".join(f"{f.nome} ({f.para_que})" for f in FONTES if f.usada == usada)


def fontes_usadas() -> str:
    return _lista(True)


def fontes_nao_usadas() -> str:
    return _lista(False)
