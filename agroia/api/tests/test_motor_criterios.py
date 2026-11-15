"""Seis critérios 0-1: fórmula, limites 0 e 1, explicação, evidências e lacunas."""
import pytest

from app.services.motor.catalogo import FaixaPalhada, catalogo_do_pais
from app.services.motor.criterios import calcular_notas, classe_do_k
from app.services.motor.declive import fator_do_declive, ls_rusle
from app.services.motor.entradas import Erodibilidade
from app.services.motor.modelo import Estrategia
from app.services.motor.relevo_service import Relevo
from motor_helpers import PLANO, clima, cultura, entradas, item


def notas(itens, culturas, **mudancas):
    e = entradas(itens, culturas, **mudancas)
    return calcular_notas(Estrategia("x", "x", "atual", tuple(itens)), e)


# --- água: ETc anual / chuva anual (chuva padrão: 1200 mm; ET0 100 mm/mês)
def kc1(id_="c", **kw):
    return cultura(id_, kc_inicial=1.0, kc_medio=1.0, kc_final=1.0, **kw)


def test_agua_meio_ano_de_kc_1_usa_metade_da_chuva():
    n, _ = notas([item("c", 1, 6)], [kc1()])
    assert n["agua"].nota == pytest.approx(0.5)
    assert "600 mm" in n["agua"].explicacao and "1200 mm" in n["agua"].explicacao


def test_agua_limites_zero_e_um():
    n, _ = notas([item("c", 1, 12, perene=True)], [kc1(perene=True)], clima=clima(chuva=50.0))  # ETc 1200 contra 600 mm
    assert n["agua"].nota == 0.0
    n, _ = notas([item("c", 1, 6)], [kc1()], clima=clima(et0=0.0))
    assert n["agua"].nota == 1.0


def test_agua_consorcio_vale_o_componente_que_mais_usa_agua():
    a, b = kc1("a"), cultura("b", kc_inicial=0.5, kc_medio=0.5, kc_final=0.5)
    n, _ = notas([item("a", 1, 6), item("b", 1, 6)], [a, b])
    assert n["agua"].nota == pytest.approx(0.5)  # não soma: 600 mm, não 900 mm


def test_agua_irrigacao_sim_diz_que_a_irrigacao_cobre_a_falta():
    n, _ = notas([item("c", 1, 6)], [kc1()], irrigacao="sim")
    assert "irrigação cobre a falta" in n["agua"].explicacao
    n, _ = notas([item("c", 1, 6)], [kc1()], irrigacao="parte")
    assert "só parte" in n["agua"].explicacao


def test_agua_evidencias_com_numero_fonte_e_periodo():
    n, _ = notas([item("c", 1, 6)], [kc1()])
    etc, chuva = n["agua"].evidencias
    assert (etc.valor, etc.unidade, chuva.valor, chuva.unidade) == (600.0, "mm", 1200.0, "mm")
    assert chuva.fonte == "NASA POWER (teste)" and chuva.periodo == "1991–2020" and "FAO-56" in etc.fonte


def test_agua_confianca_baixa_mostra_faixa_e_nao_so_um_numero():
    n, _ = notas([item("c", 1, 6)], [kc1(confianca_parametros="baixa")])
    faixa = n["agua"].evidencias[-1]
    assert faixa.valor == "300–500" and "faixa" in faixa.texto and "confiança baixa" in n["agua"].explicacao


def test_agua_sem_chuva_do_local_ou_sem_kc_e_sem_dado():
    cl = clima()
    cl.chuva_mm[3] = None
    n, lac = notas([item("c", 1, 6)], [kc1()], clima=cl)
    assert n["agua"].nota is None and lac
    n, lac = notas([item("c", 1, 6)], [cultura("c", kc_medio=None)])
    assert n["agua"].nota is None and any("Kc" in l for l in lac)


# --- terra: 0,4 x meses/12 + 0,3 x biomassa + 0,3 x fixadora
def test_terra_maximo_com_o_ano_todo_palha_alta_e_leguminosa():
    a, b = cultura("a", aporte_biomassa="alto"), cultura("b", fixa_nitrogenio=True)
    n, _ = notas([item("a", 1, 6), item("b", 7, 12)], [a, b])
    assert n["terra"].nota == pytest.approx(1.0)


def test_terra_palha_baixa_sem_leguminosa_e_seis_meses():
    n, _ = notas([item("c", 1, 6)], [cultura("c", aporte_biomassa="baixo")])
    assert n["terra"].nota == pytest.approx(0.4 * 6 / 12 + 0.3 * 0.33)


def test_terra_usa_a_maior_palha_da_rotacao():
    a, b = cultura("a", aporte_biomassa="baixo"), cultura("b", aporte_biomassa="medio")
    n, _ = notas([item("a", 1, 3), item("b", 4, 6)], [a, b])
    assert n["terra"].nota == pytest.approx(0.4 * 6 / 12 + 0.3 * 0.66)


def test_terra_classe_desconhecida_ou_vazia_e_sem_dado_com_lacuna():
    n, lac = notas([item("c", 1, 6)], [cultura("c", aporte_biomassa="enorme")])
    assert n["terra"].nota is None and any("desconhecida" in l for l in lac)
    n, lac = notas([item("c", 1, 6)], [cultura("c", aporte_biomassa=None)])
    assert n["terra"].nota is None and lac


def test_terra_aceita_a_escala_feminina():
    n, _ = notas([item("c", 1, 12)], [cultura("c", aporte_biomassa="alta")])
    assert n["terra"].nota == pytest.approx(0.4 + 0.3)


# --- erosão: 1 - (1 - parcela coberta) x fator do declive (LS da RUSLE da declividade medida; só a classe: tabela por classe)
FORTE_NO_VERAO = [10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # toda a chuva forte em jan-mar


def test_erosao_chuva_forte_toda_coberta_em_terreno_plano_da_nota_maxima():
    n, _ = notas([item("c", 1, 3)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=PLANO)
    assert n["erosao"].nota == 1.0


def test_erosao_chuva_forte_toda_descoberta_em_declive_forte_da_zero():
    n, _ = notas([item("c", 7, 9)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("montanhoso", 60.0, "SRTM"))
    assert n["erosao"].nota == 0.0
    n, _ = notas([item("c", 7, 9)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("forte_ondulado", 30.0, "SRTM"))
    assert n["erosao"].nota == 0.0


@pytest.mark.parametrize("classe, fator", [("plano", 0.22), ("suave_ondulado", 0.84), ("ondulado", 1.0), ("forte_ondulado", 1.0), ("montanhoso", 1.0)])
def test_erosao_fator_do_declive_so_pela_classe(classe, fator):
    n, _ = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo(classe, None, "q7"))
    parcela = 2 / 3
    assert n["erosao"].nota == pytest.approx(max(0.0, 1 - (1 - parcela) * fator))


def test_erosao_sem_declividade_usa_fator_medio_e_registra_lacuna():
    n, lac = notas([item("c", 7, 9)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=None)
    assert n["erosao"].nota == pytest.approx(0.5) and any("declividade" in l for l in lac)


def test_erosao_evidencias_trazem_parcela_e_declividade_com_fonte():
    n, _ = notas([item("c", 1, 3)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("plano", 1.5, "SRTM 30 m"))
    parcela, declive = n["erosao"].evidencias
    assert parcela.valor == 100.0 and parcela.unidade == "%" and (declive.valor, declive.fonte) == (1.5, "SRTM 30 m")


def test_erosao_sem_chuva_forte_no_dado_e_sem_nota():
    n, lac = notas([item("c", 1, 3)], [cultura("c")], clima=clima(forte=[None] * 12))
    assert n["erosao"].nota is None and lac


def test_erosao_cultura_fora_do_catalogo_ainda_cobre_o_solo():
    n, _ = notas([item(None, 1, 3)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=PLANO)
    assert n["erosao"].nota == 1.0


@pytest.mark.parametrize("pct, ls", [(1.5, 0.22), (5.5, 0.84), (14.0, 2.76), (32.5, 7.59), (60.0, 13.65)])
def test_ls_da_rusle_reproduz_a_tabela_da_validacao_com_rampa_de_46_m(pct, ls):
    assert ls_rusle(pct) == pytest.approx(ls, rel=0.02)  # tabela 2.5 do VALIDACAO-PARAMETROS-MOTOR.md (AH 703, razão moderada)


def test_ls_da_rusle_vale_1_na_parcela_padrao_da_usle_e_cresce_com_a_rampa():
    assert ls_rusle(9.0, 22.13) == pytest.approx(1.0, abs=0.01)  # 72,6 pés e 9 %
    assert ls_rusle(5.5, 91) == pytest.approx(1.13, rel=0.02) and ls_rusle(5.5, 23) == pytest.approx(0.64, rel=0.03)


@pytest.mark.parametrize("pct, fator", [(1.5, 0.222), (5.5, 0.846), (14.0, 1.0), (60.0, 1.0)])
def test_erosao_com_declividade_medida_usa_o_ls_com_teto_1(pct, fator):
    assert fator_do_declive(pct) == pytest.approx(fator, abs=0.002)
    n, _ = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("plano", pct, "SRTM 30 m"))
    assert n["erosao"].nota == pytest.approx(max(0.0, 1 - (1 / 3) * fator), abs=0.001)


def test_erosao_medida_vence_a_classe_e_o_texto_cita_a_declividade_e_a_fonte():
    # a classe diz "plano" (fator 0,22), mas a declividade medida de 14 % manda: fator 1
    n, _ = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("plano", 14.0, "SRTM 30 m"))
    assert n["erosao"].nota == pytest.approx(1 - 1 / 3)
    assert "declividade de 14,0% medida por satélite (SRTM)" in n["erosao"].explicacao
    declive = n["erosao"].evidencias[1]
    assert (declive.valor, declive.unidade, declive.fonte) == (14.0, "%", "SRTM 30 m")
    q7, _ = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("plano", None, "q7"))
    assert "medida por satélite" not in q7["erosao"].explicacao and q7["erosao"].evidencias[1].unidade == "classe"


def test_erosao_sem_nada_usa_o_fator_sem_dado():
    n, lac = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=None)
    assert n["erosao"].nota == pytest.approx(1 - (1 / 3) * 0.5) and any("declividade" in l for l in lac)


# --- pragas
def test_pragas_uma_cultura_so_da_zero():
    n, _ = notas([item("a", 1, 6)], [cultura("a")])
    assert n["pragas"].nota == 0.0


def test_pragas_duas_familias_distintas_dao_um():
    n, _ = notas([item("a", 1, 3), item("b", 4, 6)], [cultura("a"), cultura("b", familia_botanica="Fabaceae")])
    assert n["pragas"].nota == 1.0


def test_pragas_mesma_familia_seguida_desconta_e_nunca_fica_negativa():
    n, _ = notas([item("a", 1, 3), item("b", 4, 6)], [cultura("a"), cultura("b")])
    assert n["pragas"].nota == 0.0
    a, b = cultura("a"), cultura("b", familia_botanica="Fabaceae")
    n, _ = notas([item("a", 1, 3), item("b", 4, 6), item("a", 7, 9)], [a, b])  # P F P: (2-1)/(3-1) = 0,5; a volta P->P desconta 0,2
    assert n["pragas"].nota == pytest.approx(0.3)


def test_pragas_ordena_pelo_mes_de_inicio():
    a, b = cultura("a"), cultura("b", familia_botanica="Fabaceae")
    n1, _ = notas([item("a", 1, 3), item("a", 4, 6), item("b", 7, 9)], [a, b])
    n2, _ = notas([item("b", 7, 9), item("a", 1, 3), item("a", 4, 6)], [a, b])
    assert n1["pragas"].nota == n2["pragas"].nota


def test_pragas_sem_familia_e_lacuna():
    n, lac = notas([item("a", 1, 3), item("b", 4, 6)], [cultura("a", familia_botanica=None), cultura("b")])
    assert n["pragas"].nota == 0.0 and any("família" in l for l in lac)  # sobra 1 cultura com família
    n, _ = notas([item("a", 1, 3)], [cultura("a", familia_botanica=None)])
    assert n["pragas"].nota is None


# --- renda
@pytest.mark.parametrize("n_comerciais, esperado", [(0, 0.0), (1, 0.5), (2, 0.8), (3, 1.0), (4, 1.0)])
def test_renda_pelo_numero_de_culturas_comerciais(n_comerciais, esperado):
    itens = [item(f"c{i}", 1 + i, 1 + i) for i in range(n_comerciais)] + [item("capa", 12, 12)]
    culturas = [cultura(f"c{i}") for i in range(n_comerciais)] + [cultura("capa", tipos=("cobertura",))]
    n, _ = notas(itens, culturas)
    assert n["renda"].nota == esperado


# --- animais
@pytest.mark.parametrize("classe, esperado", [("baixo", 0.3), ("medio", 0.6), ("alto", 1.0)])
def test_animais_pela_classe_do_valor_forrageiro(classe, esperado):
    n, _ = notas([item("c", 1, 3)], [cultura("c", valor_forrageiro=classe)])
    assert n["animais"].nota == esperado


def test_animais_usa_o_maior_da_rotacao():
    n, _ = notas([item("a", 1, 3), item("b", 4, 6)], [cultura("a", valor_forrageiro="baixo"), cultura("b", valor_forrageiro="alto")])
    assert n["animais"].nota == 1.0


def test_animais_vazio_em_todas_e_ignorado_com_lacuna():
    n, lac = notas([item("a", 1, 3)], [cultura("a", valor_forrageiro=None)])
    assert n["animais"].nota is None and "Sem dado" in n["animais"].explicacao and lac


def test_animais_cultura_vazia_nao_derruba_a_que_tem_valor():
    n, _ = notas([item("a", 1, 3), item("b", 4, 6)], [cultura("a", valor_forrageiro=None), cultura("b", valor_forrageiro="medio")])
    assert n["animais"].nota == 0.6


def test_animais_valor_desconhecido_vira_lacuna_sem_chute():
    n, lac = notas([item("a", 1, 3)], [cultura("a", valor_forrageiro="superalto")])
    assert n["animais"].nota is None and any("desconhecido" in l for l in lac)


# --- cultura fora do catálogo
def test_cultura_fora_do_catalogo_vira_lacuna_e_nao_entra_nas_notas():
    n, lac = notas([item(None, 1, 3, texto="amendoim"), item("a", 4, 6)], [cultura("a")])
    assert any("amendoim" in l and "sem dados suficientes" in l.lower() for l in lac)
    assert n["renda"].nota == 0.5 and n["terra"].nota is not None


def test_so_cultura_fora_do_catalogo_deixa_as_notas_de_cultura_sem_dado():
    n, lac = notas([item(None, 1, 3, texto="amendoim")], [cultura("a")])
    assert all(n[c].nota is None for c in ("agua", "terra", "pragas", "renda", "animais"))
    assert n["erosao"].nota is not None  # o calendário sozinho já diz quando o solo está coberto


# --- erosão com a erodibilidade K do solo (SoilGrids): 1 - (1 - parcela) x fator do declive x fator do K
@pytest.mark.parametrize("k, classe, fator", [(0.0145, "baixa", 0.75), (0.02, "media", 1.0), (0.034, "media", 1.0), (0.035, "alta", 1.25), (0.05, "alta", 1.25)])
def test_erosao_fator_da_erodibilidade(k, classe, fator):
    e = Erodibilidade(k_usle=k)
    n, lac = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("suave_ondulado", None, "q7"), erodibilidade=e)
    assert classe_do_k(k) == classe
    assert n["erosao"].nota == pytest.approx(1 - (1 / 3) * 0.84 * fator)  # parcela 2/3, declive 0,84 (suave ondulado)
    assert not any("erodibilidade" in l for l in lac)


def test_erosao_sem_k_usa_fator_neutro_e_registra_lacuna():
    n, lac = notas([item("c", 1, 2)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("suave_ondulado", None, "q7"), erodibilidade=None)
    assert n["erosao"].nota == pytest.approx(1 - (1 / 3) * 0.84)  # o mesmo de antes do K
    assert any("erodibilidade" in l for l in lac)


def test_erosao_com_k_alto_em_declive_forte_nao_passa_de_zero():
    n, _ = notas([item("c", 7, 9)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("forte_ondulado", 30.0, "SRTM"), erodibilidade=Erodibilidade(0.05))
    assert n["erosao"].nota == 0.0


def test_erosao_k_alto_piora_e_k_baixo_melhora_a_nota():
    kw = dict(clima=clima(forte=FORTE_NO_VERAO), relevo=Relevo("suave_ondulado", None, "q7"))
    baixo, _ = notas([item("c", 1, 2)], [cultura("c")], erodibilidade=Erodibilidade(0.01), **kw)
    alto, _ = notas([item("c", 1, 2)], [cultura("c")], erodibilidade=Erodibilidade(0.05), **kw)
    assert baixo["erosao"].nota > alto["erosao"].nota


def test_erosao_evidencia_do_k_com_valor_unidade_e_fonte():
    n, _ = notas([item("c", 1, 3)], [cultura("c")], clima=clima(forte=FORTE_NO_VERAO), relevo=PLANO, erodibilidade=Erodibilidade(0.0145))
    k = n["erosao"].evidencias[-1]
    assert k.valor == 0.0145 and k.unidade == "t·ha·h/(ha·MJ·mm)" and k.fonte == "SoilGrids 2.0 (ISRIC)"
    assert "baixa" in k.texto and "erodibilidade baixa" in n["erosao"].explicacao


# --- regra 15: a classe da palhada vem com a faixa quando depende da época
def palha(n):
    return next(ev for ev in n["terra"].evidencias if ev.texto.startswith(("Palha ", "Palhada ")))


def test_palha_que_depende_da_epoca_mostra_a_classe_com_a_faixa():
    milho = cultura("milho", aporte_biomassa="medio", faixa_palhada=FaixaPalhada(2.1, 6.0, 9.8), depende_da_epoca={"aporte_biomassa": True})
    n, _ = notas([item("milho", 1, 3)], [milho])
    ev = palha(n)
    assert ev.texto == "Palhada de Milho: palhada média, de 2,1 a 9,8 t/ha conforme a data de manejo (depende da época)"
    assert (ev.valor, ev.unidade, ev.fonte) == ("2,1–9,8", "t/ha", "Base de culturas do Field Shift")
    assert "(palhada média, de 2,1 a 9,8 t/ha conforme a data de manejo)" in n["terra"].explicacao


@pytest.mark.parametrize("depende", [False, None])
def test_palha_que_nao_depende_da_epoca_fica_como_antes(depende):
    milho = cultura("milho", aporte_biomassa="medio", faixa_palhada=FaixaPalhada(2.1, 6.0, 9.8), depende_da_epoca={"aporte_biomassa": depende})
    n, _ = notas([item("milho", 1, 3)], [milho])
    ev = palha(n)
    assert ev.texto == "Palha que fica no campo (maior da rotação: Milho)" and (ev.valor, ev.unidade) == ("média", "classe")
    assert "t/ha" not in n["terra"].explicacao and "(classe média)" in n["terra"].explicacao


def test_palha_que_depende_da_epoca_sem_faixa_completa_fica_como_antes():
    milho = cultura("milho", aporte_biomassa="medio", faixa_palhada=FaixaPalhada(None, 6.0, None), depende_da_epoca={"aporte_biomassa": True})
    assert palha(notas([item("milho", 1, 3)], [milho])[0]).unidade == "classe"


def test_palha_do_catalogo_real_milho_do_brasil_mostra_a_faixa():
    milho = catalogo_do_pais("BR")["milho"]  # depende_da_epoca verdadeiro, faixa 3,9 a 14,5 t/ha
    ev = palha(notas([item("milho", 1, 3)], [milho])[0])
    assert ev.valor == "3,9–14,5" and ev.unidade == "t/ha"


# --- regra 16: o aviso da régua vai junto da explicação do critério
def test_aviso_da_pastagem_dos_eua_aparece_na_explicacao_de_animais_sem_duplicar_atencao():
    past = catalogo_do_pais("US")["pastagem"]
    n, _ = notas([item("pastagem", 1, 12, perene=True)], [past])
    aviso = past.avisos["valor_forrageiro"]
    assert n["animais"].explicacao.endswith(f"(classe alto). ({aviso})") and "Atenção: Atenção" not in n["animais"].explicacao
    assert n["animais"].explicacao.count("Atenção") == 1


def test_aviso_sem_atencao_no_inicio_ganha_o_prefixo_e_sem_aviso_nada_muda():
    c = cultura("c", valor_forrageiro="alto", avisos={"valor_forrageiro": "A variedade pode intoxicar o gado."})
    assert notas([item("c", 1, 3)], [c])[0]["animais"].explicacao.endswith("(Atenção: A variedade pode intoxicar o gado.)")
    sem = notas([item("c", 1, 3)], [cultura("c", valor_forrageiro="alto")])[0]["animais"].explicacao
    assert sem == "A melhor comida para os animais da rotação é a de C (classe alto)."


def test_classes_aparecem_em_portugues_de_produtor_no_texto_e_na_evidencia():
    for chave, exibida in (("baixo", "baixa"), ("medio", "média"), ("alto", "alta")):
        n, _ = notas([item("c", 1, 3)], [cultura("c", aporte_biomassa=chave)])
        assert f"(classe {exibida})" in n["terra"].explicacao and palha(n).valor == exibida
    for chave, exibida in (("nenhum", "nenhum"), ("baixo", "baixo"), ("medio", "médio"), ("alto", "alto")):
        n, _ = notas([item("c", 1, 3)], [cultura("c", valor_forrageiro=chave)])
        assert n["animais"].explicacao.endswith(f"(classe {exibida}).") and n["animais"].evidencias[0].valor == exibida
