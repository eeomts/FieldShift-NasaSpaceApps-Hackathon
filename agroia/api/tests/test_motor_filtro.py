"""Filtro: cada regra elimina com o motivo certo; a atual nunca é eliminada."""
import pytest

from app.services.motor.filtro import avaliar, fracao_de_anos_com_geada, gd_das_safras
from motor_helpers import clima, cultura, entradas, episodio, item, serie_diaria

RESP = (10, 12)  # outubro a dezembro: 3 meses


def rodar(c, e, eliminar=True, it=None):
    return avaliar([it or item(c.id, *RESP)], e, eliminar)


def e_com(c, **mudancas):
    return entradas([item(c.id, *RESP)], [c], **mudancas)


def test_cultura_excluida_pelo_produtor_elimina():
    c = cultura("soja")
    r = rodar(c, e_com(c, excluidas=frozenset({"soja"})))
    assert r.eliminada and r.motivos == ["Você disse que não planta Soja."]


def test_excluida_na_atual_nao_e_motivo():
    c = cultura("soja")
    r = rodar(c, e_com(c, excluidas=frozenset({"soja"})), eliminar=False)
    assert not r.eliminada and not r.alertas


# --- equipamento
EQUIP = {"soja": {"plantio": {"plantadeira_graos"}, "colheita": {"colhedora"}}}


def test_equipamento_falta_no_plantio_e_na_colheita():
    c = cultura("soja")
    r = rodar(c, e_com(c, equipamentos=frozenset({"manual"}), equipamentos_cultura=EQUIP))
    assert r.eliminada and len(r.motivos) == 2
    assert "plantio" in r.motivos[0] and "Plantadeira" in r.motivos[0] and "colheita" in r.motivos[1]


def test_equipamento_so_a_colheita_falta():
    c = cultura("soja")
    r = rodar(c, e_com(c, equipamentos=frozenset({"plantadeira_graos"}), equipamentos_cultura=EQUIP))
    assert len(r.motivos) == 1 and "colheita" in r.motivos[0]


def test_equipamento_basta_um_da_lista_em_cada_etapa():
    c = cultura("milho")
    eq = {"milho": {"plantio": {"plantadeira_graos", "manual"}, "colheita": {"colhedora", "manual"}}}
    assert not rodar(c, e_com(c, equipamentos=frozenset({"manual"}), equipamentos_cultura=eq)).eliminada


def test_produtor_que_nao_respondeu_equipamentos_nao_e_filtrado():
    c = cultura("soja")
    r = rodar(c, e_com(c, equipamentos=None, equipamentos_cultura=EQUIP))
    assert not r.eliminada and r.lacunas == []


def test_cultura_sem_linha_de_equipamento_nao_filtra_e_gera_lacuna():
    c = cultura("arroz_irrigado")
    r = rodar(c, e_com(c, irrigacao="sim", equipamentos=frozenset({"manual"}), equipamentos_cultura=EQUIP))
    assert not r.eliminada and any("Sem lista de máquinas" in l for l in r.lacunas)


def test_cultura_com_etapa_sem_linha_gera_lacuna_e_nao_elimina():
    c = cultura("soja")
    r = rodar(c, e_com(c, equipamentos=frozenset({"plantadeira_graos"}), equipamentos_cultura={"soja": {"plantio": {"plantadeira_graos"}}}))
    assert not r.eliminada and any("colheita" in l for l in r.lacunas)


# --- graus-dia: Tb 10 e tmed 25 dão 450 GD por mês, 1350 nos 3 meses do período
def test_graus_dia_abaixo_de_90_por_cento_elimina():
    c = cultura("c", graus_dia_ciclo_min=1501)  # 1350 / 1501 = 89,9 %
    r = rodar(c, e_com(c))
    assert r.eliminada and "graus-dia" in r.motivos[0] and "1.501" in r.motivos[0]
    assert "1.350 graus-dia na metade dos anos (2001–2020)" in r.motivos[0]


def test_graus_dia_entre_90_e_100_so_alerta():
    c = cultura("c", graus_dia_ciclo_min=1450)  # 93 %
    r = rodar(c, e_com(c))
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["limite_termico"]
    assert "validar localmente" in r.alertas[0].texto


def test_graus_dia_suficiente_passa_sem_alerta():
    c = cultura("c", graus_dia_ciclo_min=1350)
    r = rodar(c, e_com(c))
    assert not r.eliminada and not r.alertas


def test_graus_dia_na_borda_de_90_por_cento_passa_com_alerta():
    c = cultura("c", graus_dia_ciclo_min=1500)  # exatamente 90 %
    r = rodar(c, e_com(c))
    assert not r.eliminada and r.alertas


def test_mandioca_so_elimina_pelo_minimo_nunca_pelo_maximo():
    m = cultura("mandioca", graus_dia_ciclo_min=100, graus_dia_ciclo_max=200, perene=True, tipos=("comercial", "tolerante_seca"))
    it = item("mandioca", 1, 12, perene=True)
    assert not avaliar([it], entradas([it], [m]), True).eliminada  # 12 meses x 15 x 30 = 5400 GD, muito acima do máximo
    m2 = cultura("mandioca", graus_dia_ciclo_min=6500, graus_dia_ciclo_max=7000, perene=True, tipos=("comercial", "tolerante_seca"))
    assert avaliar([it], entradas([it], [m2]), True).eliminada  # abaixo do mínimo (teste de frio)


def test_sem_exigencia_de_graus_dia_nao_filtra_e_gera_lacuna_menos_na_perene():
    c = cultura("c", graus_dia_ciclo_min=None)
    r = rodar(c, e_com(c))
    assert not r.eliminada and any("graus-dia" in l for l in r.lacunas)
    p = cultura("pastagem", perene=True, graus_dia_ciclo_min=None, graus_dia_ciclo_max=None)
    it = item("pastagem", 1, 12, perene=True)
    assert not any("graus-dia" in l for l in avaliar([it], entradas([it], [p]), True).lacunas)


def test_tb_fora_de_0_a_20_vira_lacuna():
    c = cultura("c", temp_base_c=25)
    r = rodar(c, e_com(c))
    assert not r.eliminada and any("graus-dia" in l for l in r.lacunas)


def test_gd_usa_so_os_meses_do_periodo_e_a_virada_do_ano():
    c = cultura("c", graus_dia_ciclo_min=900)
    cl = clima(tmed=[10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 30, 30])  # só nov e dez têm calor
    it = item("c", 11, 2)  # nov, dez, jan, fev: 2 x 600 = 1200 GD
    assert not avaliar([it], entradas([it], [c], clima=cl), True).eliminada
    it2 = item("c", 1, 4)  # só frio: 0 GD
    assert avaliar([it2], entradas([it2], [c], clima=cl), True).eliminada


# --- graus-dia pela mediana das safras 2001–2020 (regra 2) e perenes forrageiras sem filtro (regra 14)
FRIO = 10  # tmed igual à Tb de 10: 0 GD no mês
CICLO = [20, 20, 10, 10, 10, 10, 10, 10, 10, 10, 30, 30]  # nov e dez somam 600 cada; jan e fev, 300 cada


def test_safra_que_atravessa_o_ano_soma_nov_dez_do_ano_de_plantio_e_jan_fev_do_seguinte():
    cl = clima(tmed=CICLO, tmed_por_ano={2005: [FRIO] * 10 + [30, 30]})  # em 2005, jan e fev ficam sem calor
    safras = gd_das_safras([11, 12, 1, 2], 10, cl)
    assert len(safras) == 20  # plantios de 2001 a 2020; a de 2020 usa jan e fev de 2021
    assert sorted(safras)[0] == 1200  # safra de 2004: nov-dez de 2004 (1200) + jan-fev de 2005 (0)
    assert sorted(safras)[1:] == [1800] * 19  # a safra pertence ao ano de plantio: 2005 pega jan-fev de 2006


def test_safra_sem_o_ano_seguinte_fica_de_fora():
    cl = clima(tmed=CICLO, tmed_por_ano={2021: None})
    assert len(gd_das_safras([11, 12, 1, 2], 10, cl)) == 19  # a de 2020 precisaria de jan-fev de 2021
    assert len(gd_das_safras([10, 11, 12], 10, cl)) == 20  # no mesmo ano não precisa do seguinte


def test_mediana_e_o_texto_com_numeros_periodo_e_minimo():
    c = cultura("c", graus_dia_ciclo_min=1500)
    it = item("c", 11, 2)  # 1800 GD em todas as safras
    assert not avaliar([it], entradas([it], [c], clima=clima(tmed=CICLO)), True).eliminada
    c2 = cultura("c", graus_dia_ciclo_min=2000)  # 1800 / 2000 = 90 %: não elimina, mas fica no limite
    r = avaliar([it], entradas([it], [c2], clima=clima(tmed=CICLO)), True)
    assert not r.eliminada and r.alertas[0].codigo == "limite_termico"
    assert "1.800 graus-dia na metade dos anos (2001–2020) e ela precisa de pelo menos 2.000" in r.alertas[0].texto
    c3 = cultura("c", graus_dia_ciclo_min=2100)  # 85,7 %: elimina
    assert avaliar([it], entradas([it], [c3], clima=clima(tmed=CICLO)), True).eliminada


def test_poucas_safras_viram_lacuna_e_nao_filtram():
    c = cultura("c", graus_dia_ciclo_min=9000)
    cl = clima(tmed_por_ano={a: None for a in range(2001, 2013)})  # só 8 safras (2013 a 2020)
    r = rodar(c, e_com(c, clima=cl))
    assert not r.eliminada and not r.alertas
    assert any("sem anos suficientes de clima para checar o calor do ciclo" in l for l in r.lacunas)
    cl10 = clima(tmed_por_ano={a: None for a in range(2001, 2011)})  # 10 safras: já decide
    assert rodar(c, e_com(c, clima=cl10)).eliminada


def test_p10_frio_com_mediana_boa_so_avisa_ano_frio():
    c = cultura("c", graus_dia_ciclo_min=1300)  # mediana 1350 (104 %)
    cl = clima(tmed_por_ano={a: FRIO for a in range(2001, 2005)})  # 4 anos de 20 sem calor: P10 = 0
    r = rodar(c, e_com(c, clima=cl))
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["ano_frio"]
    assert "em ano frio pode não completar o ciclo" in r.alertas[0].texto and "1.300" in r.alertas[0].texto
    um_so = clima(tmed_por_ano={2001: FRIO})  # 1 ano frio em 20: o P10 fica em 1215, acima de 90 % do mínimo (1170)
    assert not rodar(c, e_com(c, clima=um_so)).alertas


def test_a_mediana_manda_e_nao_a_media():
    c = cultura("c", graus_dia_ciclo_min=1350)
    cl = clima(tmed_por_ano={a: FRIO for a in range(2001, 2008)})  # 7 de 20 anos sem calor: a média cairia a 65 %
    r = rodar(c, e_com(c, clima=cl))
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["ano_frio"]
    muitos = clima(tmed_por_ano={a: FRIO for a in range(2001, 2013)})  # 12 de 20: a mediana cai
    assert rodar(c, e_com(c, clima=muitos)).eliminada


def test_cobertura_com_calor_abaixo_do_minimo_nunca_elimina_so_avisa():
    c = cultura("c", tipos=("cobertura",), graus_dia_ciclo_min=5000)
    r = rodar(c, e_com(c))
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["pouco_crescimento"]
    assert "pouco crescimento antes do frio ou do manejo" in r.alertas[0].texto and "5.000" in r.alertas[0].texto
    perto = cultura("c", tipos=("cobertura",), graus_dia_ciclo_min=1400)  # 96 %: avisa (cobertura não tem margem de 90 %)
    assert [a.codigo for a in rodar(perto, e_com(perto)).alertas] == ["pouco_crescimento"]
    folga = cultura("c", tipos=("cobertura",), graus_dia_ciclo_min=1350)
    assert not rodar(folga, e_com(folga)).alertas  # e sem aviso de ano frio, que é só de grão


def test_perene_forrageira_nao_tem_filtro_de_graus_dia_nem_lacuna():
    it = item("alfafa", 1, 12, perene=True)
    vazia = cultura("alfafa", perene=True, tipos=("comercial", "forrageira"), graus_dia_ciclo_min=None, graus_dia_ciclo_max=None, temp_base_c=5)
    r = avaliar([it], entradas([it], [vazia], clima=clima(tmed=FRIO)), True)
    assert not r.eliminada and not any("graus-dia" in l or "calor" in l for l in r.lacunas) and not r.alertas
    com_minimo = cultura("alfafa", perene=True, tipos=("comercial", "forrageira"), graus_dia_ciclo_min=9000)
    assert not avaliar([it], entradas([it], [com_minimo], clima=clima(tmed=FRIO)), True).eliminada


# --- calor na fase sensível (regra 11 revista): período out-dez, ciclo médio de 120 dias, semeadura em 15/out;
# terço do meio = dias 40 a 80 depois da semeadura (24/nov a 3/jan); o ano conta com 3 dias seguidos acima do limite
ANOS_30 = range(1991, 2021)
QUENTE = {"tmax": 40.0}


def calor_em(anos, n=3, mes=12, dia=1):
    return clima(serie=serie_diaria(dias=episodio(anos, mes, dia, n, **QUENTE)))


def test_calor_com_3_dias_seguidos_em_mais_de_30_por_cento_dos_anos_avisa_e_nao_elimina():
    c = cultura("milho", tmax_critica_c=33)
    r = rodar(c, e_com(c, clima=calor_em(range(1991, 2003))))  # 12 de 30 anos = 40 %
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["calor_floracao"]
    assert r.alertas[0].texto == "Milho: em 40% dos anos (1991–2020) a temperatura passou de 33 °C por 3 dias seguidos na floração (nov a jan); o calor nessa fase pode reduzir a produção."
    assert not avaliar([item("milho", *RESP)], e_com(c, clima=calor_em(range(1991, 2003))), False).eliminada  # na atual também só avisa


def test_calor_com_2_dias_seguidos_nao_conta_quando_o_catalogo_pede_3():
    c = cultura("milho", tmax_critica_c=33)
    assert not rodar(c, e_com(c, clima=calor_em(ANOS_30, n=2))).alertas  # 2 dias quentes todo ano: nada
    dois_separados = episodio(ANOS_30, 12, 1, 1, **QUENTE) | episodio(ANOS_30, 12, 3, 2, **QUENTE)  # 1 dia, folga, 2 dias: nunca 3 seguidos
    assert not rodar(c, e_com(c, clima=clima(serie=serie_diaria(dias=dois_separados)))).alertas
    assert [a.codigo for a in rodar(c, e_com(c, clima=calor_em(ANOS_30, n=3))).alertas] == ["calor_floracao"]


def test_calor_em_30_por_cento_exato_nao_avisa():
    c = cultura("milho", tmax_critica_c=33)
    assert not rodar(c, e_com(c, clima=calor_em(range(1991, 2000)))).alertas  # 9 de 30 = 30 %: não passa de 30 %


def test_calor_fora_da_fase_do_meio_nao_conta():
    c = cultura("milho", tmax_critica_c=33.5)
    assert not rodar(c, e_com(c, clima=calor_em(ANOS_30, mes=10, dia=20))).alertas  # calor no começo do ciclo (20 a 22/out)
    assert not rodar(c, e_com(c, clima=calor_em(ANOS_30, mes=1, dia=5))).alertas  # e depois do fim da fase (3/jan)
    it = item("milho", 6, 10)  # ciclo de 120 dias a partir de 15/jun: fase de 25/jul a 3/set
    cl = clima(serie=serie_diaria(dias=episodio(ANOS_30, 8, 1, 3, **QUENTE)))
    r = avaliar([it], entradas([it], [c], clima=cl), True)
    assert "33,5 °C por 3 dias seguidos na floração (jul a set)" in r.alertas[0].texto


def test_calor_na_safra_que_cruza_o_ano_usa_dias_do_ano_seguinte():
    c = cultura("milho", tmax_critica_c=33)
    it = item("milho", 11, 2)  # semeadura em 15/nov: a fase do meio vai de 25/dez a 3/fev
    cl = clima(serie=serie_diaria(dias=episodio(range(1992, 2004), 1, 10, 3, **QUENTE)))  # janeiro de 1992 a 2003 = safras de 1991 a 2002
    r = avaliar([it], entradas([it], [c], clima=cl), True)
    assert [a.codigo for a in r.alertas] == ["calor_floracao"] and "40%" in r.alertas[0].texto and "(dez a fev)" in r.alertas[0].texto


def test_tmax_critica_vazia_nao_avisa_nem_cria_lacuna():
    c = cultura("c", tmax_critica_c=None)
    r = rodar(c, e_com(c, clima=calor_em(ANOS_30, n=20)))
    assert not r.alertas and not r.eliminada and not any("calor" in l for l in r.lacunas)


def test_calor_em_perene_olha_o_ano_todo():
    p = cultura("alfafa", perene=True, tmax_critica_c=33, graus_dia_ciclo_min=None)
    it = item("alfafa", 1, 12, perene=True)
    cl = clima(serie=serie_diaria(dias=episodio(range(1991, 2006), 7, 10, 3, **QUENTE)))  # calor em julho, metade dos anos
    r = avaliar([it], entradas([it], [p], clima=cl), True)
    assert [a.codigo for a in r.alertas] == ["calor_floracao"] and "ao longo do ano" in r.alertas[0].texto


def test_ano_com_dia_sem_dado_na_fase_fica_de_fora_e_poucos_anos_viram_lacuna():
    c = cultura("milho", tmax_critica_c=33)
    # 12 anos quentes; os outros 18 têm um dia sem dado dentro da fase e saem da conta: 12 de 12 contam, avisa
    buracos = episodio([a for a in ANOS_30 if a >= 2003], 12, 10, 1, tmax=None)
    cl = clima(serie=serie_diaria(dias=episodio(range(1991, 2003), 12, 1, 3, **QUENTE) | buracos))
    r = rodar(c, e_com(c, clima=cl))
    assert "100%" in r.alertas[0].texto
    so_9_anos = clima(serie=serie_diaria(dias=episodio(range(1991, 2003), 12, 1, 3, **QUENTE) | episodio(range(2003, 2021), 12, 10, 1, tmax=None)))
    so_9_anos.serie_diaria = {a: s for a, s in so_9_anos.serie_diaria.items() if a < 2000}  # só 1991-1999: 9 anos com a fase inteira
    r = rodar(c, e_com(c, clima=so_9_anos))
    assert not r.alertas and not r.eliminada and any("sem anos suficientes de clima para checar o risco de calor" in l for l in r.lacunas)


def test_sem_serie_diaria_calor_vira_lacuna():
    c = cultura("milho", tmax_critica_c=33)
    r = rodar(c, e_com(c, clima=clima(serie={})))
    assert not r.alertas and any("temperatura máxima" in l for l in r.lacunas)


# --- frio por cultura (regra 17): ciclo médio de 120 dias, semeadura em 15/out; fase 0,5 a 0,75 = 14/dez a 13/jan
FRIO_DIA = {"tmin": -5.0}


def trigo(**mudancas):
    base = {"tmin_critica_c": 1.0, "fase_sensivel_frio": "floracao", "fase_frio_inicio_frac": 0.5, "fase_frio_fim_frac": 0.75, "sensivel_geada": True}
    return cultura("trigo", **(base | mudancas))


def frio_em(anos, n=1, mes=12, dia=20):
    return clima(serie=serie_diaria(dias=episodio(anos, mes, dia, n, **FRIO_DIA)))


def test_frio_so_conta_nos_dias_da_fase_e_o_texto_diz_frio_para_limiar_acima_de_zero():
    c = trigo()
    r = rodar(c, e_com(c, clima=frio_em(range(1991, 2003))))  # 12 de 30 anos, 20/dez dentro da fase
    assert r.eliminada and r.alertas == []
    assert r.motivos == ["Trigo: em 40% dos anos (1991–2020) a mínima ficou abaixo de 1 °C na floração (dez a jan); o frio nessa fase tira produção."]
    assert not rodar(c, e_com(c, clima=frio_em(ANOS_30, mes=11, dia=20))).eliminada  # frio antes da fase (20/nov)
    assert not rodar(c, e_com(c, clima=frio_em(ANOS_30, mes=2, dia=10))).eliminada  # e depois (10/fev)


def test_frio_em_30_por_cento_exato_nao_filtra_e_acima_filtra():
    c = trigo()
    assert not rodar(c, e_com(c, clima=frio_em(range(1991, 2000)))).eliminada  # 9 de 30
    assert rodar(c, e_com(c, clima=frio_em(range(1991, 2001)))).eliminada  # 10 de 30


def test_frio_pede_os_dias_seguidos_do_catalogo():
    c = trigo(tmin_dias_seguidos=3)
    assert not rodar(c, e_com(c, clima=frio_em(ANOS_30, n=2))).eliminada  # 2 dias seguidos não bastam
    r = rodar(c, e_com(c, clima=frio_em(ANOS_30, n=3)))
    assert r.eliminada and "abaixo de 1 °C por 3 dias seguidos na floração" in r.motivos[0]
    assert rodar(trigo(tmin_dias_seguidos=None), e_com(trigo(), clima=frio_em(ANOS_30, n=1))).eliminada  # vazio = 1 dia


def test_frio_na_safra_que_cruza_o_ano_olha_janeiro_do_ano_seguinte():
    c = trigo()  # a fase vai até 13/jan do ano seguinte
    r = rodar(c, e_com(c, clima=frio_em(range(1992, 2004), mes=1, dia=5)))  # janeiro de 1992 a 2003 = safras de 1991 a 2002
    assert r.eliminada and "40%" in r.motivos[0]
    assert not rodar(c, e_com(c, clima=frio_em(range(1992, 2004), mes=1, dia=20))).eliminada  # 20/jan já passou da fase


def test_frio_efeito_aviso_nunca_elimina_e_elimina_e_o_padrao():
    aviso = trigo(tmin_efeito="aviso")
    r = rodar(aviso, e_com(aviso, clima=frio_em(ANOS_30)))
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["frio"] and "o frio nessa fase tira produção" in r.alertas[0].texto
    assert rodar(trigo(tmin_efeito="elimina"), e_com(trigo(), clima=frio_em(ANOS_30))).eliminada
    atual = avaliar([item("trigo", *RESP)], e_com(trigo(), clima=frio_em(ANOS_30)), False)  # na rotação atual vira alerta
    assert not atual.eliminada and [a.codigo for a in atual.alertas] == ["frio"]


def test_texto_diz_geada_so_quando_o_limiar_e_de_geada():
    soja = trigo(tmin_critica_c=-2.2, fase_sensivel_frio="enchimento_grao")
    r = rodar(soja, e_com(soja, clima=clima(serie=serie_diaria(dias=episodio(ANOS_30, 12, 20, 1, tmin=-3.0)))))
    assert r.eliminada and "a mínima ficou abaixo de -2,2 °C no enchimento dos grãos" in r.motivos[0] and "a geada nessa fase tira produção" in r.motivos[0]
    zero = trigo(tmin_critica_c=0.0)  # limiar de 0 °C ainda é geada
    r0 = rodar(zero, e_com(zero, clima=clima(serie=serie_diaria(dias=episodio(ANOS_30, 12, 20, 1, tmin=-1.0)))))
    assert "a geada nessa fase tira produção" in r0.motivos[0]
    meio = trigo(tmin_critica_c=0.5)  # acima de 0 °C é frio
    assert "o frio nessa fase" in rodar(meio, e_com(meio, clima=frio_em(ANOS_30))).motivos[0]


@pytest.mark.parametrize("fase, texto", [
    ("emergencia", "na emergência"), ("vegetativo", "no crescimento"), ("floracao", "na floração"),
    ("enchimento_grao", "no enchimento dos grãos"), ("ciclo_todo", "durante o ciclo"),
])
def test_texto_da_fase_do_frio_em_linguagem_simples(fase, texto):
    c = trigo(fase_sensivel_frio=fase, fase_frio_inicio_frac=0.0, fase_frio_fim_frac=1.0)
    r = rodar(c, e_com(c, clima=frio_em(ANOS_30)))
    assert f"{texto} (out a fev)" in r.motivos[0]  # 15/out + 120 dias = 12/fev


def test_frio_em_perene_olha_o_ano_todo():
    p = cultura("alfafa", perene=True, tmin_critica_c=-10.0, graus_dia_ciclo_min=None, sensivel_geada=True)
    it = item("alfafa", 1, 12, perene=True)
    cl = clima(serie=serie_diaria(dias=episodio(range(1991, 2006), 7, 10, 1, tmin=-12.0)))
    r = avaliar([it], entradas([it], [p], clima=cl), True)  # sem frações no catálogo: cai no teste mensal (sem geada no clima), com lacuna
    assert not r.eliminada
    p2 = cultura("alfafa", perene=True, tmin_critica_c=-10.0, fase_frio_inicio_frac=0.0, fase_frio_fim_frac=1.0, fase_sensivel_frio="ciclo_todo", graus_dia_ciclo_min=None)
    r2 = avaliar([it], entradas([it], [p2], clima=cl), True)
    assert r2.eliminada and "ao longo do ano" in r2.motivos[0]


def test_ano_com_dia_sem_dado_na_fase_do_frio_fica_de_fora():
    c = trigo()
    buracos = episodio(range(2003, 2021), 12, 20, 1, tmin=None)  # 18 anos sem dado num dia da fase
    cl = clima(serie=serie_diaria(dias=episodio(range(1991, 2003), 12, 20, 1, **FRIO_DIA) | buracos))
    r = rodar(c, e_com(c, clima=cl))
    assert r.eliminada and "100%" in r.motivos[0]  # 12 de 12 anos com dado


def test_poucos_anos_com_dado_viram_lacuna_e_o_frio_nao_filtra():
    c = trigo()
    cl = clima(serie=serie_diaria(dias=episodio(range(1991, 2000), 12, 20, 1, **FRIO_DIA), anos=range(1991, 2000)))  # 9 anos: só a série até 1999
    r = rodar(c, e_com(c, clima=cl))
    assert not r.eliminada and any("sem anos suficientes de clima para checar o frio" in l for l in r.lacunas)


def test_sem_limiar_o_teste_antigo_de_geada_continua_igual():
    c = cultura("c", sensivel_geada=True)  # sem tmin_critica_c: 2 °C no terço do meio, por mês
    assert rodar(c, e_com(c, clima=clima(geada={11: 30}))).eliminada
    assert not rodar(c, e_com(c, clima=clima(geada={10: 30}))).eliminada
    assert not rodar(c, e_com(c, clima=clima(geada={11: 30}, serie={}))).lacunas  # a série diária nem é lida


def test_com_limiar_mas_sem_serie_diaria_cai_na_regra_antiga_com_lacuna():
    c = trigo()
    r = rodar(c, e_com(c, clima=clima(geada={11: 30}, serie={})))
    assert r.eliminada and r.motivos[0].startswith("Trigo: em 100% dos anos houve geada na fase de floração")  # teste mensal de 2 °C
    assert any("sem dados diários de temperatura mínima" in l for l in r.lacunas)
    sem_fracoes = trigo(fase_frio_inicio_frac=None, fase_frio_fim_frac=None)
    assert any("sem a fase do frio" in l for l in rodar(sem_fracoes, e_com(sem_fracoes, clima=clima())).lacunas)


# --- água: ET0 de 100 mm/mês e Kc 1,0 dão ETc de 300 mm nos 3 meses do período
def agua(chuva_mes, **kc):
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0, **kc)  # ETc = 300 mm nos 3 meses
    return rodar(c, e_com(c, clima=clima(chuva=chuva_mes)))


def test_agua_candidata_abaixo_de_50_por_cento_e_eliminada_com_os_mm():
    r = agua(22.0)  # 66 mm de chuva contra 300 mm: 22 %; sem irrigação a sugestão não fecha
    assert r.eliminada and r.alertas == []
    assert r.motivos == ["C: a chuva do período (66 mm) cobre só 22% da água que a cultura usa (300 mm); sem irrigação não fecha."]


def test_agua_na_atual_abaixo_de_50_por_cento_so_avisa_com_o_deficit():
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, clima=clima(chuva=22.0)), eliminar=False)  # a rotação atual nunca é eliminada pela água
    assert not r.eliminada and r.motivos == [] and [a.codigo for a in r.alertas] == ["agua_no_limite"]
    assert "água no limite" in r.alertas[0].texto and "22%" in r.alertas[0].texto and "faltam cerca de 234 mm" in r.alertas[0].texto


def test_agua_candidata_entre_50_e_80_por_cento_so_avisa():
    r = agua(60.0)
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["agua_no_limite"] and "água no limite" in r.alertas[0].texto


def test_agua_candidata_sem_irrigacao_informada_tambem_e_eliminada():
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    assert rodar(c, e_com(c, clima=clima(chuva=22.0), irrigacao=None)).eliminada


def test_agua_reserva_sem_kc_elimina_abaixo_de_50_por_cento_do_minimo_da_base():
    c = cultura("c", kc_inicial=None, kc_medio=None, kc_final=None, agua_ciclo_mm_min=300, agua_ciclo_mm_max=500)
    r = rodar(c, e_com(c, clima=clima(chuva=49.0)))  # 147 mm contra 300 mm: 49 %
    assert r.motivos == ["C: a chuva do período (147 mm) cobre só 49% da água que a cultura precisa (300 mm); sem irrigação não fecha."]
    assert not rodar(c, e_com(c, clima=clima(chuva=50.0))).eliminada  # 150 mm: 50 % exato só avisa
    assert not rodar(c, e_com(c, clima=clima(chuva=49.0), irrigacao="sim")).eliminada


def test_agua_entre_50_e_80_por_cento_alerta():
    r = agua(60.0)  # 60 %
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["agua_no_limite"]
    assert "faltam cerca de 120 mm" in r.alertas[0].texto  # 300 - 180


def test_agua_na_atual_tambem_so_avisa():
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, clima=clima(chuva=1.0)), eliminar=False)
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["agua_no_limite"]


def test_agua_na_borda_de_50_nao_elimina_e_80_nao_alerta():
    assert not agua(50.0).eliminada and agua(50.0).alertas
    assert not agua(80.0).eliminada and not agua(80.0).alertas


def test_agua_kc_por_terco_do_ciclo():
    c = cultura("c", kc_inicial=0.0, kc_medio=1.0, kc_final=0.0)  # 3 meses: só o mês do meio usa água (100 mm)
    cl = clima(chuva=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 0])  # chuva só no mês do meio (novembro)
    r = rodar(c, e_com(c, clima=cl))
    assert not r.eliminada and not r.alertas  # 100 mm de chuva contra 100 mm de ETc


def test_agua_ciclo_de_cinco_meses_divide_os_meses_nos_tercos():
    from app.services.motor.hidrico import etc_mensal

    c = cultura("c", kc_inicial=0.0, kc_medio=1.0, kc_final=0.0)
    etc = etc_mensal(item("c", 1, 5), c, clima(et0=90))
    esperado = {1: 0.0, 2: 30.0, 3: 90.0, 4: 30.0, 5: 0.0}  # o 2º terço (Kc 1) pega 1/3 dos meses 2 e 4 e o mês 3 inteiro
    assert {m: round(v, 6) for m, v in etc.items()} == esperado


def test_irrigacao_sim_nao_filtra_agua():
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, clima=clima(chuva=1.0), irrigacao="sim"))
    assert not r.eliminada and not r.alertas


def test_irrigacao_parte_so_alerta_mesmo_na_candidata_muito_seca():
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, clima=clima(chuva=1.0), irrigacao="parte"))  # candidata (eliminar=True) a 1 %: com irrigação em parte, só avisa
    assert not r.eliminada and r.alertas[0].codigo == "agua_no_limite" and "irrigada" in r.alertas[0].texto


def test_sem_kc_usa_a_faixa_de_agua_da_base_como_reserva():
    c = cultura("c", kc_inicial=None, kc_medio=None, kc_final=None, agua_ciclo_mm_min=300, agua_ciclo_mm_max=500)
    r = rodar(c, e_com(c, clima=clima(chuva=99.0)))  # 297 mm < 300 mm: não elimina, avisa com o déficit
    assert not r.eliminada and r.alertas[0].codigo == "agua_no_limite" and "faltam cerca de 3 mm" in r.alertas[0].texto
    r = rodar(c, e_com(c, clima=clima(chuva=130.0)))  # 390 mm: entre o mínimo e o máximo
    assert not r.eliminada and r.alertas[0].codigo == "agua_no_limite"
    r = rodar(c, e_com(c, clima=clima(chuva=200.0)))  # 600 mm: acima do máximo
    assert not r.eliminada and not r.alertas


def test_sem_kc_e_sem_faixa_vira_lacuna():
    c = cultura("c", kc_inicial=None, kc_medio=None, kc_final=None, agua_ciclo_mm_min=None, agua_ciclo_mm_max=None)
    r = rodar(c, e_com(c, clima=clima(chuva=0.0)))
    assert not r.eliminada and any("água" in l for l in r.lacunas)


def test_perene_compara_com_a_chuva_do_ano():
    p = cultura("pastagem", perene=True, kc_medio=1.0)
    it = item("pastagem", 1, 12, perene=True)
    r = avaliar([it], entradas([it], [p], clima=clima(chuva=60.0)), True)  # 720 mm contra 1200 mm: 60 %, avisa, não elimina
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["agua_no_limite"] and "faltam cerca de 480 mm" in r.alertas[0].texto
    r = avaliar([it], entradas([it], [p], clima=clima(chuva=40.0)), True)  # 480 mm contra 1200 mm: 40 %, a sugestão é eliminada
    assert r.eliminada and "480 mm" in r.motivos[0] and "1200 mm" in r.motivos[0]
    r = avaliar([it], entradas([it], [p], clima=clima(chuva=100.0)), True)
    assert not r.eliminada and not r.alertas


# --- geada
def test_geada_mais_de_30_por_cento_dos_anos_elimina_cultura_sensivel():
    c = cultura("c", sensivel_geada=True)
    r = rodar(c, e_com(c, clima=clima(geada={11: 10})))  # 10 de 30 anos = 33 %
    assert r.eliminada and "geada" in r.motivos[0] and "33%" in r.motivos[0]


def test_geada_em_30_por_cento_passa_e_cultura_nao_sensivel_ignora():
    c = cultura("c", sensivel_geada=True)
    assert not rodar(c, e_com(c, clima=clima(geada={11: 9}))).eliminada  # 30 % exatos
    n = cultura("c", sensivel_geada=False)
    assert not rodar(n, e_com(n, clima=clima(geada={11: 30}))).eliminada


def test_geada_fora_dos_meses_do_periodo_nao_conta():
    c = cultura("c", sensivel_geada=True)
    assert not rodar(c, e_com(c, clima=clima(geada={7: 30}))).eliminada


def test_geada_conta_o_ano_uma_vez_mesmo_com_geada_em_dois_meses():
    cl = clima(geada={10: 9, 11: 9})  # os mesmos 9 primeiros anos
    assert fracao_de_anos_com_geada([10, 11, 12], cl) == 9 / 30


def test_geada_sem_dado_vira_lacuna():
    c = cultura("c", sensivel_geada=True)
    cl = clima()
    cl.geada_por_ano = {}
    r = rodar(c, e_com(c, clima=cl))
    assert not r.eliminada and any("geada" in l for l in r.lacunas)


# --- arroz irrigado (regra 8)
def test_arroz_irrigado_so_passa_com_irrigacao_sim():
    c = cultura("arroz_irrigado", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    for irrigacao in ("nao", "parte", None):
        r = rodar(c, e_com(c, irrigacao=irrigacao, clima=clima(chuva=1000.0)))
        assert r.eliminada and "irrigação ou várzea" in r.motivos[0]
    assert not rodar(c, e_com(c, irrigacao="sim")).eliminada


def test_arroz_irrigado_sem_irrigacao_continua_eliminado_mesmo_com_chuva_de_sobra():
    c = cultura("arroz_irrigado", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, irrigacao="nao", clima=clima(chuva=1000.0)))
    assert r.eliminada and [a.codigo for a in r.alertas] == []


def test_arroz_irrigado_nao_passa_pelo_filtro_de_agua():
    c = cultura("arroz_irrigado", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, irrigacao="sim", clima=clima(chuva=0.0)))
    assert not r.eliminada and not r.alertas


# --- a atual nunca é eliminada: os problemas viram alertas
def test_na_atual_os_motivos_viram_alertas():
    c = cultura("c", graus_dia_ciclo_min=5000, sensivel_geada=True, kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    e = e_com(c, clima=clima(chuva=1.0, geada={11: 30}), equipamentos=frozenset({"manual"}), equipamentos_cultura={"c": {"plantio": {"x"}, "colheita": {"y"}}})
    r = avaliar([item("c", *RESP)], e, eliminar=False)
    assert not r.eliminada and r.motivos == []
    assert {a.codigo for a in r.alertas} == {"graus_dia", "agua_no_limite", "geada", "equipamento"}


def test_cultura_fora_do_catalogo_nao_e_avaliada():
    e = entradas([item(None, 10, 12)], [cultura("c")])
    assert avaliar([item(None, 10, 12)], e, True).motivos == []


# --- geada só na fase sensível: o terço do meio do ciclo (meses inteiros que tocam esse terço)
def test_geada_so_conta_no_terco_do_meio_do_periodo():
    c = cultura("c", sensivel_geada=True)  # período out-dez: o terço do meio é novembro
    assert not rodar(c, e_com(c, clima=clima(geada={10: 30}))).eliminada  # geada no início do ciclo
    assert not rodar(c, e_com(c, clima=clima(geada={12: 30}))).eliminada  # e no fim
    r = rodar(c, e_com(c, clima=clima(geada={11: 30})))
    assert r.eliminada and "floração" in r.motivos[0] and "nov" in r.motivos[0]


def test_trigo_jun_out_nao_e_barrado_por_geada_so_no_comeco_e_no_fim_do_ciclo():
    trigo = cultura("trigo", sensivel_geada=True)
    it = item("trigo", 6, 10)  # 5 meses: a floração toca jul, ago e set
    cl = clima(geada={6: 30, 10: 30})  # geada todo ano só em junho e outubro
    assert not avaliar([it], entradas([it], [trigo], clima=cl), True).eliminada
    r = avaliar([it], entradas([it], [trigo], clima=cl), False)
    assert not r.alertas
    cl2 = clima(geada={8: 30})  # geada frequente em agosto, no meio do ciclo
    r2 = avaliar([it], entradas([it], [trigo], clima=cl2), True)
    assert r2.eliminada and "floração" in r2.motivos[0] and "ago" in r2.motivos[0]
    r3 = avaliar([it], entradas([it], [trigo], clima=cl2), False)  # na atual vira alerta, com a fase no texto
    assert [a.codigo for a in r3.alertas] == ["geada"] and "floração" in r3.alertas[0].texto


def test_geada_em_cultura_perene_olha_o_ano_todo():
    p = cultura("pastagem", perene=True, sensivel_geada=True, graus_dia_ciclo_min=None, kc_medio=0.1)
    it = item("pastagem", 1, 12, perene=True)
    assert avaliar([it], entradas([it], [p], clima=clima(geada={7: 15})), True).eliminada
