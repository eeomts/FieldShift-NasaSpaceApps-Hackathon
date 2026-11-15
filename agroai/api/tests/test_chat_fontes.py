"""Testa que a instrução do agente diz quais fontes o chat usa, quais só o painel mostra e quais o app ainda não usa."""
from datetime import date
from types import SimpleNamespace

from app.services.agente.fontes_status import FONTES
from app.services.agente.prompt import montar_instrucao

_USUARIO = SimpleNamespace(idioma="pt", fazenda=None)


def _trechos(texto: str) -> dict[str, str]:
    inicio = texto.index("Dados que o AgroAI usa hoje:")
    painel = texto.index("Mostrados só no painel", inicio)
    nao = texto.index("Ainda não usa:", painel)
    fim = texto.index("Se a base de conhecimento falar", nao)
    return {"chat": texto[inicio:painel], "painel": texto[painel:nao], "nao": texto[nao:fim]}


def test_regra_das_fontes_existe():
    texto = montar_instrucao(_USUARIO, date(2026, 1, 1))
    assert "Se a base de conhecimento falar de uma fonte que o AgroAI ainda não usa" in texto
    assert "Nunca diga que um número veio de uma fonte que o app não usa." in texto
    assert "{fontes_" not in texto


def test_fontes_nas_listas_certas():
    trechos = _trechos(montar_instrucao(_USUARIO, date(2026, 1, 1)))
    assert {f.uso for f in FONTES} == {"chat", "painel", "nao"}
    for f in FONTES:
        for uso, trecho in trechos.items():
            assert (f"{f.nome} (" in trecho) == (f.uso == uso), (f.nome, uso)


def test_satelites_do_painel_nao_aparecem_como_nao_usados():
    trechos = _trechos(montar_instrucao(_USUARIO, date(2026, 1, 1)))
    for nome in ("GPM IMERG", "SMAP", "MODIS", "Open-Meteo"):
        assert nome in trechos["painel"]
        assert nome not in trechos["chat"] and nome not in trechos["nao"]
    assert "NASA POWER" in trechos["chat"]


def test_soilgrids_esta_em_usa_hoje_com_o_que_entrega():
    trechos = _trechos(montar_instrucao(_USUARIO, date(2026, 1, 1)))
    assert "SoilGrids (solo por ponto: textura, matéria orgânica, pH, erodibilidade; mapa global de 250 m)" in trechos["chat"]
    assert "SoilGrids" not in trechos["nao"]
