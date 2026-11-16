"""Registro das fontes de dados que o app usa de fato; atualizar a cada integração nova."""
from dataclasses import dataclass
from typing import Literal

# chat: o assistente consulta; painel: só o Dashboard mostra (o chat não tem esses números); nao: o app ainda não usa
Uso = Literal["chat", "painel", "nao"]


@dataclass(frozen=True)
class FonteStatus:
    nome: str
    para_que: str
    uso: Uso


FONTES: list[FonteStatus] = [
    FonteStatus(
        "NASA POWER",
        "clima mensal da célula de ~50 km desde 1991: chuva, temperatura, geada, calor, chuva forte e sequência seca; "
        "a evapotranspiração (ET0) é calculada pelo AgroAI com o método FAO-56",
        "chat",
    ),
    FonteStatus("base de culturas do AgroAI", "parâmetros de 17 culturas no Brasil e de 18 nos EUA, com fontes", "chat"),
    FonteStatus("textos da base de conhecimento do AgroAI", "explicações de conceitos", "chat"),
    FonteStatus("respostas do produtor no cadastro da fazenda", "ficha da fazenda", "chat"),
    FonteStatus("comparação de rotações do AgroAI", "notas de água, terra, erosão, pragas, renda e animais para a rotação atual e alternativas", "chat"),
    FonteStatus("SRTM", "declividade do terreno, usada na comparação de rotações", "chat"),
    FonteStatus("SoilGrids", "solo por ponto: textura, matéria orgânica, pH, erodibilidade; mapa global de 250 m", "chat"),
    FonteStatus(
        "USDA NASS, datas de plantio (Handbook 628)",
        "janelas de semeadura dos EUA (NASS Agricultural Handbook 628) transcritas no catálogo de culturas (data/catalogo/eua/culturas.csv), não lidas ao vivo; "
        "o motor só sugere uma cultura nos meses em que ela costuma ser semeada",
        "chat",
    ),
    FonteStatus("GPM IMERG", "chuva diária de satélite dos últimos 30 dias, ~10 km (se faltar, o painel usa a chuva diária do NASA POWER)", "painel"),
    FonteStatus("SMAP", "umidade do solo de hoje comparada com os mesmos dias dos anos anteriores", "painel"),
    FonteStatus("MODIS", "NDVI, o verde da lavoura no último ano, a cada 16 dias, 250 m", "painel"),
    FonteStatus("Open-Meteo", "previsão do tempo dos próximos 7 dias", "painel"),
    FonteStatus("IBGE PAM", "produção agrícola por município", "nao"),
    FonteStatus("ZARC", "janelas de plantio", "nao"),
    FonteStatus("USDA NASS, produção por condado", "área e produção por condado nos EUA (o app ainda não usa esses números)", "nao"),
]


def _lista(uso: Uso) -> str:
    return "; ".join(f"{f.nome} ({f.para_que})" for f in FONTES if f.uso == uso)


def fontes_usadas() -> str:
    return _lista("chat")


def fontes_do_painel() -> str:
    return _lista("painel")


def fontes_nao_usadas() -> str:
    return _lista("nao")
