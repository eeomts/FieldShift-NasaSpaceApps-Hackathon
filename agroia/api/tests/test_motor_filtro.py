"""Filtro: cada regra elimina com o motivo certo; a atual nunca é eliminada."""
from app.services.motor.filtro import avaliar, fracao_de_anos_com_calor, fracao_de_anos_com_geada, gd_das_safras
from motor_helpers import clima, cultura, entradas, item

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


# --- calor na fase sensível (regra 11): período out-dez, floração = novembro; só avisa
def test_calor_acima_de_30_por_cento_dos_anos_avisa_e_nao_elimina():
    c = cultura("milho", tmax_critica_c=33)
    r = rodar(c, e_com(c, clima=clima(calor={11: 12})))  # 12 de 30 anos = 40 %
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["calor_floracao"]
    assert r.alertas[0].texto == "Milho: em 40% dos anos (1991–2020) a temperatura passou de 33 °C na floração (nov); o calor nessa fase pode reduzir a produção."
    assert not avaliar([item("milho", *RESP)], e_com(c, clima=clima(calor={11: 12})), False).eliminada  # na atual também só avisa


def test_calor_em_30_por_cento_exato_nao_avisa():
    c = cultura("milho", tmax_critica_c=33)
    assert not rodar(c, e_com(c, clima=clima(calor={11: 9}))).alertas  # 9 de 30 = 30 %: não passa de 30 %


def test_calor_fora_da_floracao_nao_conta_e_fase_de_varios_meses_vira_intervalo():
    c = cultura("milho", tmax_critica_c=33.5)
    assert not rodar(c, e_com(c, clima=clima(calor={10: 30, 12: 30}))).alertas  # calor só no começo e no fim do ciclo
    it = item("milho", 6, 10)  # 5 meses: a floração toca jul, ago e set
    r = avaliar([it], entradas([it], [c], clima=clima(calor={8: 30})), True)
    assert "33,5 °C na floração (jul a set)" in r.alertas[0].texto


def test_tmax_critica_vazia_nao_avisa_nem_cria_lacuna():
    c = cultura("c", tmax_critica_c=None)
    r = rodar(c, e_com(c, clima=clima(calor={10: 30, 11: 30, 12: 30})))
    assert not r.alertas and not r.eliminada and not any("calor" in l for l in r.lacunas)


def test_calor_em_perene_olha_o_ano_todo():
    p = cultura("alfafa", perene=True, tmax_critica_c=33, graus_dia_ciclo_min=None)
    it = item("alfafa", 1, 12, perene=True)
    r = avaliar([it], entradas([it], [p], clima=clima(calor={7: 15})), True)  # calor em julho, metade dos anos
    assert [a.codigo for a in r.alertas] == ["calor_floracao"] and "ao longo do ano" in r.alertas[0].texto


def test_ano_com_mes_sem_dado_de_tmax_fica_de_fora_e_sem_dado_nenhum_vira_lacuna():
    c = cultura("milho", tmax_critica_c=33)
    cl = clima(calor={11: 12})  # 12 de 30 anos quentes
    for ano in list(cl.tmax_absoluta_por_ano)[12:]:  # os 18 anos sem calor ficam sem dado em novembro: sobram os 12 quentes
        cl.tmax_absoluta_por_ano[ano][11] = None
    assert fracao_de_anos_com_calor([11], 33, cl) == 1.0
    cl.tmax_absoluta_por_ano = {}
    r = rodar(c, e_com(c, clima=cl))
    assert not r.alertas and any("temperatura máxima" in l for l in r.lacunas)


# --- água: ET0 de 100 mm/mês e Kc 1,0 dão ETc de 300 mm nos 3 meses do período
def agua(chuva_mes, **kc):
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0, **kc)  # ETc = 300 mm nos 3 meses
    return rodar(c, e_com(c, clima=clima(chuva=chuva_mes)))


def test_agua_chuva_abaixo_de_50_por_cento_nao_elimina_e_avisa_o_deficit():
    r = agua(49.0)  # 147 mm de chuva contra 300 mm: 49 %; o sequeiro não é eliminado pela água (regra 1)
    assert not r.eliminada and r.motivos == []
    assert [a.codigo for a in r.alertas] == ["agua_no_limite"]
    texto = r.alertas[0].texto
    assert "água no limite" in texto and "49%" in texto and "faltam cerca de 153 mm" in texto  # 300 - 147


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


def test_irrigacao_parte_so_alerta():
    c = cultura("c", kc_inicial=1.0, kc_medio=1.0, kc_final=1.0)
    r = rodar(c, e_com(c, clima=clima(chuva=1.0), irrigacao="parte"))
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
    r = avaliar([it], entradas([it], [p], clima=clima(chuva=40.0)), True)  # 480 mm contra 1200 mm: avisa, não elimina
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["agua_no_limite"] and "faltam cerca de 720 mm" in r.alertas[0].texto
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
