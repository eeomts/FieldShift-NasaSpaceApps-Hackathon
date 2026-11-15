"""Filtro: cada regra elimina com o motivo certo; a atual nunca é eliminada."""
from datetime import date, timedelta

from app.services.motor.filtro import avaliar, fracao_de_anos_com_geada, janela_do_frio
from motor_helpers import ANOS, clima, cultura, entradas, item, serie_tmin

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
    assert r.eliminada and "graus-dia" in r.motivos[0] and "1501" in r.motivos[0]


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


# --- frio por fase (regra 17): limiar da cultura, só nos dias da fase, dias seguidos
def com_frio(c, it, dias, valor=-5.0, base=20.0, comeco=0, anos=ANOS, ausente=()):
    """Tmin diária: `base` em todo dia; `dias` dias seguidos a `valor`, `comeco` dias depois do início da fase, nos `anos`.

    `ausente` = dias (offset desde o início da fase) sem dado em todos os anos.
    """
    frias, falta = set(), set()
    for a in ANOS:
        ini, fim = janela_do_frio(c, it, a)
        if a in anos:
            frias |= {ini + timedelta(days=comeco + i) for i in range(dias)}
        falta |= {ini + timedelta(days=o) for o in ausente}
    return serie_tmin(lambda d: None if d in falta else (valor if d in frias else base))


def frio(c, it, serie, eliminar=True):
    return avaliar([it], entradas([it], [c], clima=clima(tmin_por_dia=serie)), eliminar)


SOJA = dict(sensivel_geada=True, tmin_critica_c=-2.2, fase_sensivel_frio="enchimento_grao", fase_frio_inicio_frac=0.73, fase_frio_fim_frac=1.0)
ARROZ = dict(sensivel_geada=True, tmin_critica_c=15, fase_sensivel_frio="floracao", fase_frio_inicio_frac=0.59, fase_frio_fim_frac=0.72, tmin_dias_seguidos=3, tmin_efeito="aviso")


def test_frio_soja_com_minima_de_0_grau_nao_sai_porque_o_limiar_e_menos_2_2():
    c = cultura("soja", **SOJA)
    it = item("soja", *RESP)
    r = frio(c, it, com_frio(c, it, dias=60, valor=0.0))  # 0 °C seria geada de 2 °C, mas não passa de -2,2
    assert not r.eliminada and not r.alertas and not r.lacunas


def test_frio_soja_abaixo_do_limiar_na_fase_elimina_com_o_texto_de_geada():
    c = cultura("soja", **SOJA)
    it = item("soja", *RESP)
    r = frio(c, it, com_frio(c, it, dias=1, valor=-3.0, comeco=5))  # a janela é o fim do ciclo
    assert r.eliminada and "geada" in r.motivos[0] and "enchimento dos grãos" in r.motivos[0] and "100%" in r.motivos[0]
    assert "-2,2" in r.motivos[0]
    na_atual = frio(c, it, com_frio(c, it, dias=1, valor=-3.0), eliminar=False)
    assert not na_atual.eliminada and [a.codigo for a in na_atual.alertas] == ["geada"]


def test_frio_a_30_por_cento_dos_anos_passa_e_acima_elimina():
    c = cultura("soja", **SOJA)
    it = item("soja", *RESP)
    assert not frio(c, it, com_frio(c, it, 1, valor=-3.0, anos=list(ANOS)[:9])).eliminada  # 9 de 30
    assert frio(c, it, com_frio(c, it, 1, valor=-3.0, anos=list(ANOS)[:10])).eliminada  # 10 de 30


def test_frio_arroz_15_graus_3_dias_com_2_dias_frios_nao_conta():
    c = cultura("arroz", **ARROZ)
    it = item("arroz", *RESP)
    r = frio(c, it, com_frio(c, it, dias=2, valor=10.0))
    assert not r.eliminada and not r.alertas and not r.lacunas


def test_frio_arroz_com_3_dias_seguidos_vira_aviso_de_frio_e_nao_elimina():
    c = cultura("arroz", **ARROZ)
    it = item("arroz", *RESP)
    r = frio(c, it, com_frio(c, it, dias=3, valor=10.0))
    assert not r.eliminada
    [a] = r.alertas
    assert a.codigo == "frio" and "frio na florada em 100% dos anos" in a.texto and "3 dias seguidos" in a.texto
    assert "geada" not in a.texto and "15 °C" in a.texto


def test_frio_dia_sem_dado_quebra_a_sequencia_e_tira_o_ano_da_conta():
    c = cultura("arroz", **ARROZ)
    it = item("arroz", *RESP)
    # 3 dias frios com o do meio sem dado, em todos os anos: nenhum ano tem a janela completa
    r = frio(c, it, com_frio(c, it, dias=3, valor=10.0, ausente=[1]))
    assert not r.eliminada and not r.alertas and any("sem a mínima diária" in l for l in r.lacunas)
    # sem dado só em 20 anos: os 10 restantes (todos frios) decidem
    serie = com_frio(c, it, dias=3, valor=10.0)
    for a in list(ANOS)[:20]:
        serie[janela_do_frio(c, it, a)[0]] = None
    assert [x.codigo for x in frio(c, it, serie).alertas] == ["frio"]


def test_frio_trigo_com_geada_so_fora_da_janela_da_fase_passa():
    c = cultura("trigo", sensivel_geada=True, tmin_critica_c=1, fase_sensivel_frio="floracao", fase_frio_inicio_frac=0.59, fase_frio_fim_frac=0.73)
    it = item("trigo", 6, 10)
    ini, fim = janela_do_frio(c, it, 2000)
    assert (fim - ini).days > 10
    # geada todo ano nos 10 dias antes da fase e nos 10 depois dela
    serie_fora = serie_tmin(lambda d: -2.0 if any(
        (a := janela_do_frio(c, it, ano)) and ((a[0] - timedelta(days=10)) <= d < a[0] or a[1] < d <= (a[1] + timedelta(days=10))) for ano in (d.year, d.year - 1)
    ) else 10.0)
    r = frio(c, it, serie_fora)
    assert not r.eliminada and not r.alertas and not r.lacunas
    assert frio(c, it, com_frio(c, it, 1, valor=-2.0, comeco=3)).eliminada  # um dia dentro da fase, todo ano


def test_frio_janela_que_vira_o_ano():
    c = cultura("c", sensivel_geada=True, tmin_critica_c=0, fase_sensivel_frio="floracao", fase_frio_inicio_frac=0.3, fase_frio_fim_frac=0.5, tmin_dias_seguidos=3)
    it = item("c", 11, 3)  # semeadura em 15/nov, ciclo médio 120: a fase vai de ~21/dez a ~14/jan
    ini, fim = janela_do_frio(c, it, 2000)
    assert (ini.year, ini.month, fim.year, fim.month) == (2000, 12, 2001, 1)
    # 3 dias seguidos: 30/dez, 31/dez e 1/jan (a virada do ano está dentro da sequência)
    serie = serie_tmin(lambda d: -1.0 if (d.month, d.day) in {(12, 30), (12, 31), (1, 1)} else 10.0)
    r = frio(c, it, serie)
    assert r.eliminada and "geada" in r.motivos[0] and "3 dias seguidos" in r.motivos[0]
    # a 2020 usa dias de 2021, que a série tem; com só 2 dias por ano, não conta
    serie2 = serie_tmin(lambda d: -1.0 if (d.month, d.day) in {(12, 31), (1, 1)} else 10.0)
    assert not frio(c, it, serie2).eliminada


def test_frio_sem_dado_diario_vira_lacuna_nao_elimina_e_nao_cai_nos_2_graus():
    c = cultura("soja", **SOJA)
    it = item("soja", *RESP)
    r = avaliar([it], entradas([it], [c], clima=clima(geada={11: 30, 12: 30, 1: 30})), True)  # geada < 2 °C todo ano, mas sem Tmin diária
    assert not r.eliminada and not r.alertas
    assert r.lacunas == ["Soja: sem a mínima diária do local para a fase enchimento dos grãos, não checamos o frio."]


def test_frio_sem_tmin_critica_mantem_a_reserva_de_2_graus_no_terco_do_meio():
    c = cultura("c", sensivel_geada=True)  # sem tmin_critica_c
    it = item("c", *RESP)
    serie = serie_tmin(lambda d: -10.0)  # a série diária é ignorada
    assert not avaliar([it], entradas([it], [c], clima=clima(tmin_por_dia=serie)), True).eliminada
    assert avaliar([it], entradas([it], [c], clima=clima(geada={11: 30}, tmin_por_dia=serie)), True).eliminada


def test_frio_fase_vazia_usa_o_ciclo_todo_e_perene_o_ano_todo():
    c = cultura("c", sensivel_geada=True, tmin_critica_c=0)
    it = item("c", *RESP)
    ini, fim = janela_do_frio(c, it, 2000)
    assert ini == date(2000, 10, 15) and (fim - ini).days == 120
    p = cultura("pastagem", perene=True, sensivel_geada=True, tmin_critica_c=-3.3, fase_sensivel_frio="ciclo_todo")
    ip = item("pastagem", 1, 12, perene=True)
    assert janela_do_frio(p, ip, 2000) == (date(2000, 1, 1), date(2000, 12, 31))
    r = frio(p, ip, serie_tmin(lambda d: -4.0 if (d.month, d.day) == (7, 1) else 10.0))
    assert r.eliminada and "geada" in r.motivos[0] and "ao longo do ano" in r.motivos[0]
