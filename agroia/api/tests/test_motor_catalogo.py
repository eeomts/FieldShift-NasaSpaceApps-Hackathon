"""Catálogo do motor: BR (17 culturas, vazio = None), EUA sem CSV e equipamentos por cultura."""
import logging

import pytest

from app.services import catalogo as base_do_app
from app.services.motor import catalogo
from app.services.motor.catalogo import catalogo_do_pais, equipamentos_por_cultura, ler_catalogo


@pytest.fixture(autouse=True)
def limpa_cache():
    catalogo_do_pais.cache_clear()
    yield
    catalogo_do_pais.cache_clear()


def test_catalogo_br_tem_as_17_culturas_e_todas_existem_na_base_do_app():
    c = catalogo_do_pais("BR")
    assert len(c) == 17
    assert set(c) <= set(base_do_app.culturas())
    assert "arroz_irrigado" in c and "arroz" in c


def test_soja_tipada():
    soja = catalogo_do_pais("BR")["soja"]
    assert soja.pais == "BR"
    assert soja.familia_botanica == "Fabaceae"
    assert soja.tipos == ("comercial", "fixadora_n")
    assert soja.tem_tipo("fixadora_n") and not soja.tem_tipo("cobertura")
    assert soja.perene is False and soja.sensivel_geada is True
    assert soja.graus_dia_ciclo_min == 1600.0 and soja.temp_base_c == 10.0 and soja.kc_medio == 1.15
    assert soja.codigo_pam == "40124"
    assert len(soja.fontes) >= 2
    assert soja.nome_zarc is None  # vazio no CSV: None, nunca "" nem 0


def test_celula_vazia_vira_none_e_nao_zero(tmp_path):
    csv = tmp_path / "culturas.csv"
    csv.write_text(
        "id,nome,tipos,perene,ciclo_dias_min,graus_dia_ciclo_max,valor_forrageiro,fixa_nitrogenio,codigo_nass,coluna_nova\n"
        "milho,Milho,comercial,false,,,,,SWEET,x\n",
        encoding="utf-8",
    )
    milho = ler_catalogo(csv, "US")["milho"]
    assert milho.ciclo_dias_min is None and milho.graus_dia_ciclo_max is None
    assert milho.valor_forrageiro is None and milho.fixa_nitrogenio is None
    assert milho.perene is False
    assert milho.codigo_nass == "SWEET" and milho.pais == "US"
    assert milho.extras == {"coluna_nova": "x"}
    assert milho.kc_medio is None  # coluna que nem existe no arquivo


def test_eua_sem_csv_devolve_vazio_e_avisa(monkeypatch, tmp_path, caplog):
    monkeypatch.setitem(catalogo.CSV_POR_PAIS, "US", tmp_path / "eua" / "culturas.csv")
    with caplog.at_level(logging.WARNING):
        assert catalogo_do_pais("US") == {}
    assert "US" in caplog.text


def test_pais_desconhecido_e_erro():
    with pytest.raises(ValueError):
        catalogo_do_pais("AR")  # type: ignore[arg-type]


def test_equipamentos_por_cultura():
    eq = equipamentos_por_cultura()
    assert set(eq["soja"]) == {"plantio", "colheita"}
    assert "colhedora" in eq["soja"]["colheita"] and "plantadeira_graos" in eq["soja"]["plantio"]
    assert all(c in base_do_app.culturas() for c in eq)
    assert all(e in base_do_app.equipamentos() for etapas in eq.values() for es in etapas.values() for e in es)
