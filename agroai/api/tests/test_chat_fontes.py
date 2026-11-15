"""Testa que a instrução do agente diz quais fontes o app usa e quais ainda não."""
from datetime import date
from types import SimpleNamespace

from app.services.agente.fontes_status import FONTES
from app.services.agente.prompt import montar_instrucao

_USUARIO = SimpleNamespace(idioma="pt", fazenda=None)


def _trechos(texto: str) -> tuple[str, str]:
    inicio = texto.index("Dados que o AgroAI usa hoje:")
    meio = texto.index("Ainda não usa:", inicio)
    fim = texto.index("Se a base de conhecimento falar", meio)
    return texto[inicio:meio], texto[meio:fim]


def test_regra_das_fontes_existe():
    texto = montar_instrucao(_USUARIO, date(2026, 1, 1))
    assert "Se a base de conhecimento falar de uma fonte que o AgroAI ainda não usa" in texto
    assert "Nunca diga que um número veio de uma fonte que o app não usa." in texto
    assert "{fontes_" not in texto


def test_fontes_nas_listas_certas():
    usadas, nao_usadas = _trechos(montar_instrucao(_USUARIO, date(2026, 1, 1)))
    assert any(f.usada for f in FONTES) and any(not f.usada for f in FONTES)
    for f in FONTES:
        assert (f.nome in usadas) == f.usada
        assert (f.nome in nao_usadas) != f.usada


def test_imerg_esta_em_ainda_nao_usa():
    usadas, nao_usadas = _trechos(montar_instrucao(_USUARIO, date(2026, 1, 1)))
    assert "GPM IMERG" in nao_usadas
    assert "GPM IMERG" not in usadas
    assert "NASA POWER" in usadas


def test_soilgrids_esta_em_usa_hoje_com_o_que_entrega():
    usadas, nao_usadas = _trechos(montar_instrucao(_USUARIO, date(2026, 1, 1)))
    assert "SoilGrids (solo por ponto: textura, matéria orgânica, pH, erodibilidade; mapa global de 250 m)" in usadas
    assert "SoilGrids" not in nao_usadas
