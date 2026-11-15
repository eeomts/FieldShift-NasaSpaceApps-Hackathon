"""Catálogo do motor: BR (17) e EUA (18), vazio = None, janela, régua das evidências e equipamentos."""
import csv
import logging
from dataclasses import replace

import pytest

from app.core.caminhos import RAIZ_REPO
from app.services import catalogo as base_do_app
from app.services.motor import catalogo
from app.services.motor.catalogo import (
    ArranjoRegional,
    FaixaPalhada,
    catalogo_do_pais,
    classe_da_palhada,
    cultura_no_estado,
    equipamentos_por_cultura,
    janela_de_semeadura,
    ler_catalogo,
)


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


def test_catalogo_eua_tem_as_18_culturas_e_todas_existem_na_base_do_app():
    c = catalogo_do_pais("US")
    assert len(c) == 18
    assert set(c) <= set(base_do_app.culturas())
    assert all(x.pais == "US" for x in c.values())


def test_mes_dia_do_csv_vira_tupla_e_vazio_e_none(tmp_path):
    csv = tmp_path / "culturas.csv"
    csv.write_text(
        "id,nome,tipos,semeadura_inicio,semeadura_fim,manejo_inicio,manejo_fim,tipo_manejo\n"
        "aveia,Aveia,cobertura,08-15,09-15,,02-29,morte_pelo_frio\n",
        encoding="utf-8",
    )
    a = ler_catalogo(csv, "US")["aveia"]
    assert a.semeadura_inicio == (8, 15) and a.semeadura_fim == (9, 15)
    assert a.manejo_inicio is None and a.manejo_fim == (2, 29)
    assert a.tipo_manejo == "morte_pelo_frio"
    assert "semeadura_inicio" not in a.extras and "tipo_manejo" not in a.extras


@pytest.mark.parametrize("valor", ["8-15", "13-01", "02-30", "ago-15", "08/15", "08-155"])
def test_mes_dia_invalido_e_erro_claro(tmp_path, valor):
    csv = tmp_path / "culturas.csv"
    csv.write_text(f"id,nome,tipos,semeadura_fim\naveia,Aveia,cobertura,{valor}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="aveia.*semeadura_fim.*MM-DD"):
        ler_catalogo(csv, "US")


def test_condicao_semeadura_e_textos_viram_tupla_e_texto(tmp_path):
    csv = tmp_path / "culturas.csv"
    csv.write_text(
        "id,nome,tipos,condicao_semeadura,lacuna_informacao,risco_revisao_local\n"
        "aveia,Aveia,cobertura,apos_cereal_inverno| apos_silagem,Falta medição.,Confirme com o agrônomo.\n"
        "milho,Milho,comercial,,,\n",
        encoding="utf-8",
    )
    c = ler_catalogo(csv, "US")
    assert c["aveia"].condicao_semeadura == ("apos_cereal_inverno", "apos_silagem")
    assert c["aveia"].lacuna_informacao == "Falta medição." and c["aveia"].risco_revisao_local == "Confirme com o agrônomo."
    assert c["milho"].condicao_semeadura == () and c["milho"].lacuna_informacao is None


def test_e_cobertura():
    c = catalogo_do_pais("BR")
    assert c["aveia"].e_cobertura and c["crotalaria"].e_cobertura
    assert not c["soja"].e_cobertura
    assert catalogo_do_pais("US")["pastagem"].e_cobertura is False  # forrageira sem o tipo cobertura


def test_csv_real_traz_janela_e_condicao_semeadura():
    crot = catalogo_do_pais("BR")["crotalaria"]
    assert crot.semeadura_inicio == (10, 1) and crot.semeadura_fim == (3, 31)  # janela que cruza o ano
    assert crot.tipo_manejo == "corte" and crot.condicao_semeadura == ("apos_colheita_graos",)
    assert crot.lacuna_informacao and crot.risco_revisao_local
    aveia_us = catalogo_do_pais("US")["aveia"]
    assert aveia_us.condicao_semeadura == ("apos_cereal_inverno", "apos_silagem", "a_lanco_lavoura_em_pe")
    assert catalogo_do_pais("BR")["soja"].semeadura_inicio is None


def test_avisos_da_pastagem_dos_eua_carregam():
    p = catalogo_do_pais("US")["pastagem"]
    assert "festuca" in p.avisos["valor_forrageiro"]
    assert catalogo_do_pais("US")["milho"].avisos == {}


def test_arranjos_do_trevo_dos_eua_trazem_estados_e_numeros():
    arr = {a.nome: a for a in catalogo_do_pais("US")["trevo"].arranjos}
    assert arr["alabama"].estados == ("AL",) and arr["tennessee"].estados == ("TN",)
    al = arr["alabama"]
    assert al.regional and (al.ciclo_dias_min, al.ciclo_dias_max) == (116, 256)
    assert (al.graus_dia_ciclo_min, al.graus_dia_ciclo_max) == (800, 2650)
    assert (al.agua_ciclo_mm_min, al.agua_ciclo_mm_max) == (90, 430)
    assert al.semeadura_inicio == (8, 25) and al.manejo_fim == (5, 8) and al.tipo_manejo == "dessecacao"
    assert al.origem["agua_ciclo_mm"] == "calculo"


def test_arranjos_regionais_com_estados_e_palhada():
    c = catalogo_do_pais("US")
    mi = c["feijao"].arranjos[0]
    assert (mi.nome, mi.estados) == ("michigan", ("MI",))
    assert mi.palhada is not None and mi.palhada.tipico == 5.16
    assert c["algodao"].arranjos[0].estados == ("GA",) and c["algodao"].arranjos[0].semeadura_inicio == (5, 2)
    assert c["cevada"].arranjos[0].estados == ("MT",)
    assert c["ervilhaca"].arranjos[0].estados == ("GA",)
    br = catalogo_do_pais("BR")
    assert br["crotalaria"].arranjos[0].estados == ("RS",)
    assert br["milheto"].arranjos[0].estados == ("GO", "MG", "MS", "MT", "SP")
    assert br["nabo_forrageiro"].arranjos[0].estados == ("GO", "DF", "MT", "MG")
    assert br["soja"].arranjos == ()


def test_arranjos_de_consorcio_da_pastagem_nao_sao_regionais():
    past = catalogo_do_pais("BR")["pastagem"]
    por_nome = {a.nome: a for a in past.arranjos}
    assert set(por_nome) == {"braquiaria_solteira", "consorcio_milho_safrinha"}
    assert not por_nome["consorcio_milho_safrinha"].regional and not por_nome["braquiaria_solteira"].regional
    assert past.arranjos_regionais == ()
    cons = por_nome["consorcio_milho_safrinha"]
    assert cons.palhada.minimo == 2.85 and cons.palhada.maximo == 4.65 and cons.palhada.tipico is None
    assert cons.estados == ("GO", "MT", "MS", "PR")


def test_faixa_de_palhada_e_depende_da_epoca():
    c = catalogo_do_pais("BR")
    soja = c["soja"]
    assert (soja.faixa_palhada.minimo, soja.faixa_palhada.tipico, soja.faixa_palhada.maximo) == (2.5, 4.0, 5.6)
    assert soja.depende_da_epoca == {"aporte_biomassa": False, "cobertura_solo": True}
    assert catalogo_do_pais("US")["alfafa"].faixa_palhada is None  # tudo null no arquivo: "não sei"
    assert catalogo_do_pais("US")["alfafa"].depende_da_epoca == {"aporte_biomassa": None, "cobertura_solo": None}


def test_evidencia_ausente_ou_sem_regua_nao_quebra(tmp_path):
    (tmp_path / "evidencias").mkdir()
    (tmp_path / "evidencias" / "milho.json").write_text('{"valores": {}}', encoding="utf-8")
    csv = tmp_path / "culturas.csv"
    csv.write_text("id,nome,tipos\nsoja,Soja,comercial\nmilho,Milho,comercial\n", encoding="utf-8")
    for cultura in ler_catalogo(csv, "BR").values():
        assert cultura.avisos == {} and cultura.depende_da_epoca == {} and cultura.arranjos == ()
        assert cultura.faixa_palhada is None


def test_evidencia_com_json_invalido_e_erro_claro(tmp_path):
    (tmp_path / "evidencias").mkdir()
    (tmp_path / "evidencias" / "soja.json").write_text("{quebrado", encoding="utf-8")
    csv = tmp_path / "culturas.csv"
    csv.write_text("id,nome,tipos\nsoja,Soja,comercial\n", encoding="utf-8")
    with pytest.raises(ValueError, match="soja.json"):
        ler_catalogo(csv, "BR")


# --- regra 13: arranjos regionais
def test_trevo_dos_eua_em_al_usa_o_arranjo_alabama_e_fora_dele_usa_a_linha():
    trevo = catalogo_do_pais("US")["trevo"]
    al = cultura_no_estado(trevo, "AL")
    assert al.arranjo_aplicado == "alabama" and (al.ciclo_dias_min, al.ciclo_dias_max) == (116, 256)
    assert (al.graus_dia_ciclo_min, al.graus_dia_ciclo_max, al.agua_ciclo_mm_min, al.agua_ciclo_mm_max) == (800, 2650, 90, 430)
    assert al.semeadura_inicio == (8, 25) and al.manejo_fim == (5, 8) and al.tipo_manejo == "dessecacao"
    assert janela_de_semeadura(al).inicio == (8, 25)  # a janela da regra 12 lê a cultura já trocada
    assert cultura_no_estado(trevo, "TN").arranjo_aplicado == "tennessee" and cultura_no_estado(trevo, "TN").ciclo_dias_min == 172
    for outro in ("GA", "IA", None):  # GA é a região de referência da linha
        c = cultura_no_estado(trevo, outro)
        assert c is trevo and c.arranjo_aplicado is None and c.ciclo_dias_min == 149


def test_ervilhaca_em_ga_usa_a_janela_e_a_palhada_do_arranjo_e_mantem_o_resto_da_linha():
    erv = catalogo_do_pais("US")["ervilhaca"]
    ga = cultura_no_estado(erv, "GA")
    assert ga.semeadura_inicio == (9, 15) and ga.semeadura_fim == (11, 1) and ga.manejo_inicio == (3, 8) and ga.ciclo_dias_min == 127
    assert ga.condicao_semeadura == erv.condicao_semeadura  # o arranjo não traz: fica a da linha
    assert erv.aporte_biomassa == "baixo" and ga.aporte_biomassa == "medio"  # típico 4,32 t/ha recalcula a classe
    assert ga.faixa_palhada.tipico == 4.32
    assert ga.confianca_parametros == erv.confianca_parametros and ga.nome == erv.nome


def test_arranjo_sem_um_campo_mantem_o_da_linha():
    algodao = catalogo_do_pais("US")["algodao"]
    ga = cultura_no_estado(algodao, "GA")
    assert ga.arranjo_aplicado == "georgia" and ga.semeadura_inicio == (5, 2)  # só a semeadura vem do arranjo
    assert (ga.ciclo_dias_min, ga.graus_dia_ciclo_min, ga.aporte_biomassa, ga.faixa_palhada) == (130, 1270, "baixo", algodao.faixa_palhada)
    trevo_al = cultura_no_estado(catalogo_do_pais("US")["trevo"], "AL")  # arranjo sem palhada: classe e faixa da linha
    assert trevo_al.aporte_biomassa == "medio" and trevo_al.faixa_palhada.tipico == 3.25


def test_consorcio_e_outro_sistema_nunca_sao_aplicados_como_regionais():
    br = catalogo_do_pais("BR")
    for estado in ("GO", "MT", "MS", "PR"):  # estados do consórcio da pastagem
        assert cultura_no_estado(br["pastagem"], estado) is br["pastagem"]
    milheto = br["milheto"]  # "primavera" é outro sistema nos mesmos estados da linha, não uma região
    assert not milheto.arranjos[0].regional and cultura_no_estado(milheto, "GO") is milheto


def test_classe_da_palhada_pelos_limites_da_regua():
    assert [classe_da_palhada(t) for t in (0.5, 2.29, 2.3, 5.99, 6.0, 12.4)] == ["baixo", "baixo", "medio", "medio", "alto", "alto"]


def test_palhada_do_arranjo_sem_tipico_mantem_a_classe_da_linha():
    base = replace(catalogo_do_pais("BR")["soja"], aporte_biomassa="baixo")
    com_tipico = replace(base, arranjos=(ArranjoRegional("a", ("GO",), palhada=FaixaPalhada(5, 6.5, 8)),))
    sem_tipico = replace(base, arranjos=(ArranjoRegional("a", ("GO",), palhada=FaixaPalhada(5, None, 8)),))
    assert cultura_no_estado(com_tipico, "GO").aporte_biomassa == "alto"
    r = cultura_no_estado(sem_tipico, "GO")
    assert r.aporte_biomassa == "baixo" and r.faixa_palhada.maximo == 8


def test_cultura_vale_no_estado_do_arranjo_mesmo_fora_de_estados_validos():
    us = catalogo_do_pais("US")
    for id_, estado in (("cevada", "MT"), ("feijao", "MI"), ("ervilhaca", "GA"), ("trevo", "AL"), ("trevo", "TN")):
        linha = us[id_]
        assert not linha.vale_em(estado), (id_, estado)
        assert cultura_no_estado(linha, estado).vale_em(estado), (id_, estado)
    assert cultura_no_estado(us["trevo"], "AL").vale_em("GA")  # a região da linha continua valendo
    assert not cultura_no_estado(us["trevo"], "AL").vale_em("IA")
    assert cultura_no_estado(catalogo_do_pais("BR")["crotalaria"], "RS").vale_em("RS")


def test_mais_de_um_arranjo_regional_no_mesmo_estado_usa_o_primeiro_e_registra(caplog):
    soja = catalogo_do_pais("BR")["soja"]
    dois = replace(soja, arranjos=(ArranjoRegional("a", ("GO",), ciclo_dias_min=1), ArranjoRegional("b", ("GO",), ciclo_dias_min=2)))
    with caplog.at_level(logging.WARNING):
        r = cultura_no_estado(dois, "GO")
    assert r.arranjo_aplicado == "a" and r.ciclo_dias_min == 1 and "2 arranjos regionais" in caplog.text


def test_dados_reais_nao_repetem_estado_entre_arranjos_regionais():
    for pais in ("BR", "US"):
        for c in catalogo_do_pais(pais).values():
            estados = [e for a in c.arranjos_regionais for e in a.estados]
            assert len(estados) == len(set(estados)), c.id
