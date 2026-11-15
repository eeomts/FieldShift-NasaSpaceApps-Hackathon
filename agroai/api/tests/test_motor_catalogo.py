"""Catálogo do motor: BR (17 culturas, vazio = None), EUA sem CSV e equipamentos por cultura."""
import csv
import importlib.util
import logging
from dataclasses import replace

import pytest

from app.core.caminhos import RAIZ_REPO
from app.services import catalogo as base_do_app
from app.services.motor import catalogo
from app.services.motor.catalogo import catalogo_do_pais, equipamentos_por_cultura, ler_catalogo
from app.services.motor.parametros import FASES_FRIO_TEXTO


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
    assert soja.nome_zarc == "Soja"
    assert catalogo_do_pais("BR")["crotalaria"].nome_zarc is None  # vazio no CSV: None, nunca "" nem 0


def test_nome_zarc_multivalor_e_aveia_sem_zarc():
    c = catalogo_do_pais("BR")
    assert c["milho"].nome_zarc == "Milho 1ª Safra|Milho 2ª Safra"  # posição 1 = 1ª safra, 2 = 2ª safra
    assert c["aveia"].nome_zarc is None  # aveia-preta de cobertura: fora do ZARC de propósito


def test_nome_zarc_do_catalogo_bate_com_o_mapa_do_zarc():
    c = catalogo_do_pais("BR")
    with open(RAIZ_REPO / "data" / "brasil" / "zarc" / "mapa_culturas_zarc.csv", encoding="utf-8", newline="") as f:
        mapa = {linha["cultura_id"]: (linha["nome_zarc"].strip() or None) for linha in csv.DictReader(f)}
    assert mapa, "mapa do ZARC vazio"
    for cultura_id, nome_zarc in mapa.items():
        assert cultura_id in c, f"{cultura_id} do mapa não está no catálogo"
        assert c[cultura_id].nome_zarc == nome_zarc, cultura_id


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


def test_estados_validos_vira_tupla_em_maiuscula_e_vazio_e_sem_restricao(tmp_path):
    csv = tmp_path / "culturas.csv"
    csv.write_text(
        "id,nome,tipos,estados_validos\n"
        "trevo,Trevo,cobertura,ga| al\n"
        "milho,Milho,comercial,\n",
        encoding="utf-8",
    )
    c = ler_catalogo(csv, "US")
    assert c["trevo"].estados_validos == ("GA", "AL") and "estados_validos" not in c["trevo"].extras
    assert c["trevo"].vale_em("GA") and not c["trevo"].vale_em("IA") and c["trevo"].vale_em(None)
    assert c["milho"].estados_validos == () and c["milho"].vale_em("IA") and c["milho"].vale_em(None)


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


def test_tmin_critica_c_e_os_campos_de_frio_sao_lidos_como_numero_do_csv_real():
    c = catalogo_do_pais("BR")
    soja = c["soja"]
    assert soja.tmin_critica_c == -2.2 and soja.fase_frio_inicio_frac == 0.73 and soja.fase_frio_fim_frac == 1.0
    assert soja.fase_sensivel_frio == "enchimento_grao" and soja.tmin_dias_seguidos is None and soja.tmin_efeito is None
    arroz = c["arroz_irrigado"]
    assert arroz.tmin_critica_c == 15.0 and arroz.tmin_dias_seguidos == 3.0 and arroz.tmin_efeito == "aviso"
    assert c["mandioca"].tmin_critica_c is None  # sem limiar com fonte: vazio, nunca 0
    assert catalogo_do_pais("US")["trigo"].fase_frio_inicio_frac == 0.87
    for pais in ("BR", "US"):
        for cultura in catalogo_do_pais(pais).values():
            assert cultura.tmin_critica_c is None or isinstance(cultura.tmin_critica_c, float)
            assert not {"tmin_critica_c", "fase_sensivel_frio", "tmin_efeito", "semeadura_inicio", "condicao_semeadura"} & set(cultura.extras)
    assert c["milheto"].semeadura_inicio == "01-21" and c["milheto"].condicao_semeadura == "apos_colheita_graos|a_lanco_lavoura_em_pe"


def test_campos_de_frio_com_virgula_decimal_e_celula_vazia(tmp_path):
    csv = tmp_path / "culturas.csv"
    csv.write_text(
        "id,nome,tipos,tmin_critica_c,fase_frio_inicio_frac,tmin_dias_seguidos,tmin_efeito\n"
        'soja,Soja,comercial,"-2,2",0.73,,\n'
        "arroz,Arroz,comercial,15,0.59,3,aviso\n",
        encoding="utf-8",
    )
    c = ler_catalogo(csv, "BR")
    assert c["soja"].tmin_critica_c == -2.2 and c["soja"].tmin_dias_seguidos is None and c["soja"].tmin_efeito is None
    assert c["soja"].fase_frio_fim_frac is None  # coluna que nem existe no arquivo
    assert c["arroz"].tmin_dias_seguidos == 3.0 and c["arroz"].tmin_efeito == "aviso" and not c["arroz"].extras


# --- M4: o nome da cultura no motor é o de exibição do culturas.json; o do CSV fica em nome_base
def test_nome_do_motor_e_o_de_exibicao_do_json_e_o_do_csv_vai_para_nome_base():
    eua = catalogo_do_pais("US")
    assert (eua["soja"].nome, eua["soja"].nome_base) == ("Soja", "Soja (soybean)")
    assert (eua["pastagem"].nome, eua["pastagem"].nome_base) == ("Pasto", "Festuca alta (tall fescue)")
    br = catalogo_do_pais("BR")
    assert (br["aveia"].nome, br["aveia"].nome_base) == ("Aveia", "Aveia-preta")
    assert (br["pastagem"].nome, br["pastagem"].nome_base) == ("Pasto", "Braquiária")
    for pais in ("BR", "US"):
        for c in catalogo_do_pais(pais).values():
            assert c.nome == base_do_app.nome_exibicao(base_do_app.culturas()[c.id], "pt") and "(" not in c.nome
            assert c.nome_base


def test_cultura_fora_do_json_mantem_o_nome_do_csv(tmp_path):
    arquivo = tmp_path / "culturas.csv"
    arquivo.write_text("id,nome,tipos\nmaxixe,Maxixe (gherkin),comercial\nsoja,Soja (soybean),comercial\n", encoding="utf-8")
    c = ler_catalogo(arquivo, "US")
    assert (c["maxixe"].nome, c["maxixe"].nome_base) == ("Maxixe (gherkin)", "Maxixe (gherkin)")
    assert (c["soja"].nome, c["soja"].nome_base) == ("Soja", "Soja (soybean)")


def test_dias_seguidos_de_frio_vazio_vale_1_e_arredonda():
    c = catalogo_do_pais("BR")
    assert c["soja"].tmin_dias_seguidos is None and c["soja"].dias_seguidos_de_frio == 1
    assert c["arroz_irrigado"].dias_seguidos_de_frio == 3
    assert replace(c["soja"], tmin_dias_seguidos=0.0).dias_seguidos_de_frio == 1
    assert replace(c["soja"], tmin_dias_seguidos=2.6).dias_seguidos_de_frio == 3


# --- M2: o texto do frio cobre as fases e os valores que o montar_csv.py aceita
def _montar_csv():
    spec = importlib.util.spec_from_file_location("montar_csv_motor_catalogo", RAIZ_REPO / "data" / "catalogo" / "scripts" / "montar_csv.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_fases_de_frio_com_texto_sao_as_do_montar_csv():
    assert set(FASES_FRIO_TEXTO) == _montar_csv().FASES_FRIO - {""}


def test_fase_e_efeito_de_frio_dos_dois_csv_sao_permitidos():
    montar = _montar_csv()
    for pais in ("BR", "US"):
        for c in catalogo_do_pais(pais).values():
            assert (c.fase_sensivel_frio or "") in montar.FASES_FRIO, (pais, c.id)
            assert (c.tmin_efeito or "") in montar.EFEITOS_FRIO, (pais, c.id)
            assert c.fase_sensivel_frio is None or c.fase_sensivel_frio in FASES_FRIO_TEXTO, (pais, c.id)  # com texto próprio, não o genérico
