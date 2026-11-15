"""Fases do ciclo em dias: semeadura no dia 15, ciclo médio (com arranjo), perene o ano todo e dias seguidos."""
from datetime import date

from app.services.motor.catalogo import ArranjoRegional, catalogo_do_pais, cultura_no_estado
from app.services.motor.fases import anos_com_sequencia, ciclo_em_dias, datas_da_fase, meses_da_fase
from motor_helpers import cultura, episodio, item, serie_diaria


def test_ciclo_e_a_media_de_min_e_max_com_reserva_no_periodo_do_item():
    assert ciclo_em_dias(cultura("c", ciclo_dias_min=100, ciclo_dias_max=140), item("c", 10, 12)) == 120
    assert ciclo_em_dias(cultura("c", ciclo_dias_min=100, ciclo_dias_max=None), item("c", 10, 12)) == 100
    assert ciclo_em_dias(cultura("c", ciclo_dias_min=None, ciclo_dias_max=None), item("c", 10, 12)) == 3 * 30.4


def test_ciclo_usa_o_arranjo_regional_ja_aplicado():
    trevo = catalogo_do_pais("US")["trevo"]
    al = cultura_no_estado(trevo, "AL")  # arranjo alabama: ciclo de 116 a 256 dias
    assert ciclo_em_dias(trevo, item("trevo", 9, 3)) == (149 + 226) / 2
    assert ciclo_em_dias(al, item("trevo", 9, 3)) == 186


def test_fase_em_dias_a_partir_da_semeadura_no_dia_15():
    c = cultura("c", ciclo_dias_min=100, ciclo_dias_max=140)  # ciclo médio de 120 dias
    assert datas_da_fase(item("c", 10, 12), c, 2001, 0.0, 1.0) == (date(2001, 10, 15), date(2002, 2, 12))  # cruza o ano
    assert datas_da_fase(item("c", 10, 12), c, 2001, 1 / 3, 2 / 3) == (date(2001, 11, 24), date(2002, 1, 3))
    assert meses_da_fase(item("c", 10, 12), c, 1 / 3, 2 / 3) == "nov a jan"
    assert meses_da_fase(item("c", 3, 5), cultura("c", ciclo_dias_min=10, ciclo_dias_max=10), 0.0, 1.0) == "mar"


def test_perene_vai_de_1_de_janeiro_a_31_de_dezembro_e_sem_mes_de_inicio_nao_ha_fase():
    assert datas_da_fase(item("p", 1, 12, perene=True), cultura("p"), 2005, 0.2, 0.4) == (date(2005, 1, 1), date(2005, 12, 31))
    assert datas_da_fase(item("p", None, None), cultura("p"), 2005, 0.0, 1.0) is None


def test_dias_seguidos_dentro_da_fase_e_ano_sem_dado_fica_de_fora():
    c = cultura("c", ciclo_dias_min=100, ciclo_dias_max=140)
    it = item("c", 10, 12)
    frio = episodio(range(1991, 2001), 12, 1, 3, tmin=-4.0)  # 10 anos com 3 dias de -4 °C
    serie = serie_diaria(dias=frio | episodio([2005], 12, 1, 1, tmin=None))  # em 2005 falta um dia dentro da fase
    assert anos_com_sequencia(it, c, serie, "tmin_c", 0.0, 1.0, lambda t: t < 0, 3) == (10, 29)
    assert anos_com_sequencia(it, c, serie, "tmin_c", 0.0, 1.0, lambda t: t < 0, 4) == (0, 29)  # 4 seguidos: ninguém
    assert anos_com_sequencia(it, c, {}, "tmin_c", 0.0, 1.0, lambda t: t < 0, 1) == (0, 0)  # sem série
