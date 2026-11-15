"""Explicação: 'por que' só com ganho de 0,1 ou mais, confiança (a menor) e lacunas."""
from app.services.motor.catalogo import catalogo_do_pais
from app.services.motor.explicacao import avisos_da_regua, confianca, por_que
from app.services.motor.modelo import CRITERIOS, NotaCriterio
from motor_helpers import cultura, item


def notas(**v) -> dict[str, NotaCriterio]:
    return {c: NotaCriterio(c, v.get(c), "") for c in CRITERIOS}


PESOS = {c: 1 / 6 for c in CRITERIOS}


def test_por_que_so_inclui_criterio_que_ganha_por_pelo_menos_0_1():
    atual = notas(agua=0.50, terra=0.50, erosao=0.50)
    nova = notas(agua=0.60, terra=0.599, erosao=0.40)
    frases = por_que(nova, atual, PESOS)
    assert len(frases) == 1 and "água" in frases[0] and "0,60" in frases[0] and "0,50" in frases[0]


def test_por_que_vazio_quando_nao_ganha_em_nada():
    assert por_que(notas(agua=0.5), notas(agua=0.5), PESOS) == []


def test_por_que_no_maximo_3_frases_mais_pesadas_primeiro():
    atual = notas(agua=0.0, terra=0.0, erosao=0.0, pragas=0.0)
    nova = notas(agua=0.2, terra=0.2, erosao=0.2, pragas=0.2)
    pesos = {"agua": 0.1, "terra": 0.4, "erosao": 0.3, "pragas": 0.2, "renda": 0, "animais": 0}
    frases = por_que(nova, atual, pesos)
    assert len(frases) == 3 and "terra" in frases[0] and "erosão" in frases[1] and "pragas" in frases[2]


def test_por_que_ignora_criterio_sem_nota_em_um_dos_lados():
    assert por_que(notas(animais=1.0), notas(animais=None), PESOS) == []
    assert por_que(notas(animais=None), notas(animais=0.1), PESOS) == []


def test_confianca_e_a_menor_das_culturas():
    cs = {"a": cultura("a", confianca_parametros="alta"), "b": cultura("b", confianca_parametros="media"), "c": cultura("c", confianca_parametros="baixa")}
    assert confianca((item("a", 1, 3),), cs) == ("alta", [])
    assert confianca((item("a", 1, 3), item("b", 4, 6)), cs)[0] == "media"
    assert confianca((item("a", 1, 3), item("b", 4, 6), item("c", 7, 9)), cs)[0] == "baixa"


def test_confianca_sem_valor_na_base_e_baixa_com_lacuna():
    c, lac = confianca((item("a", 1, 3),), {"a": cultura("a", confianca_parametros=None)})
    assert c == "baixa" and lac


def test_confianca_sem_nenhuma_cultura_da_base_e_baixa_com_lacuna():
    c, lac = confianca((item(None, 1, 3),), {})
    assert c == "baixa" and lac


def test_confianca_cultura_fora_do_catalogo_nao_derruba_as_demais():
    assert confianca((item(None, 1, 3), item("a", 4, 6)), {"a": cultura("a")})[0] == "alta"


def test_onde_piora_so_inclui_criterio_que_perde_por_pelo_menos_0_1():
    from app.services.motor.explicacao import onde_piora

    atual = notas(agua=0.12, terra=0.50, erosao=0.50)
    nova = notas(agua=0.0, terra=0.41, erosao=0.60)
    frases = onde_piora(nova, atual, PESOS)
    assert frases == ["Usa mais água: nota 0,00 contra 0,12 da sua rotação atual."]  # terra perde só 0,09; erosão ganha


def test_onde_piora_no_maximo_3_frases_mais_pesadas_primeiro_e_ignora_sem_nota():
    from app.services.motor.explicacao import onde_piora

    atual = notas(agua=0.5, terra=0.5, erosao=0.5, pragas=0.5, animais=0.5)
    nova = notas(agua=0.0, terra=0.0, erosao=0.0, pragas=0.0, animais=None)
    pesos = {"agua": 0.1, "terra": 0.4, "erosao": 0.3, "pragas": 0.2, "renda": 0, "animais": 0}
    frases = onde_piora(nova, atual, pesos)
    assert len(frases) == 3 and "terra" in frases[0] and "erosão" in frases[1] and "famílias" in frases[2]
    assert onde_piora(atual, nova, pesos) == []


# --- regra 10: confiança baixa traz o que não sabemos e o que confirmar
def test_confianca_baixa_traz_os_dois_textos_da_cultura_do_catalogo_real():
    br = catalogo_do_pais("BR")
    conf, lac = confianca((item("crotalaria", 10, 12),), br)
    c = br["crotalaria"]
    assert conf == "baixa" and lac == [f"Crotalária: {c.lacuna_informacao}", f"Crotalária: {c.risco_revisao_local}"]


def test_confianca_alta_ou_media_nao_traz_os_textos_mesmo_se_preenchidos():
    for nivel in ("alta", "media"):
        c = cultura("c", confianca_parametros=nivel, lacuna_informacao="Falta medição.", risco_revisao_local="Confirme.")
        assert confianca((item("c", 1, 3),), {"c": c}) == (nivel, [])
    br = catalogo_do_pais("BR")
    assert confianca((item("feijao", 1, 3), item("soja", 4, 8)), br)[1] == []  # catálogo real, confiança alta e média


def test_texto_vazio_nao_cria_lacuna_vazia_e_a_cultura_repetida_nao_duplica():
    vazia = cultura("c", confianca_parametros="baixa", lacuna_informacao=None, risco_revisao_local="")
    assert confianca((item("c", 1, 3),), {"c": vazia}) == ("baixa", [])
    so_lacuna = cultura("d", confianca_parametros="baixa", lacuna_informacao="Falta medição.")
    assert confianca((item("d", 1, 3), item("d", 6, 8)), {"d": so_lacuna})[1] == ["D: Falta medição."]


def test_confianca_nao_informada_mantem_a_lacuna_antiga():
    c = cultura("c", confianca_parametros=None, lacuna_informacao="Falta.")
    conf, lac = confianca((item("c", 1, 3),), {"c": c})
    assert conf == "baixa" and lac == ["C: confiança dos parâmetros não informada; tratada como baixa."]


# --- regra 16: avisos da régua viram alerta aviso_<coluna>
def test_aviso_da_pastagem_dos_eua_vira_alerta_so_com_a_cultura_na_rotacao():
    us = catalogo_do_pais("US")
    a = avisos_da_regua((item("pastagem", 3, 9), item("milho", 10, 2)), us)
    assert [x.codigo for x in a] == ["aviso_valor_forrageiro"]
    assert a[0].texto == "Festuca alta (tall fescue): " + us["pastagem"].avisos["valor_forrageiro"].removeprefix("Atenção: ")  # o alerta já é um aviso
    assert a[0].texto.startswith("Festuca alta (tall fescue): a maioria dos pastos antigos")
    assert avisos_da_regua((item("milho", 10, 2),), us) == []  # sem aviso, sem alerta


def test_aviso_so_aparece_se_a_classe_da_coluna_aparece():
    c = cultura("c", avisos={"valor_forrageiro": "Cuidado.", "cobertura_solo": "Outro."}, valor_forrageiro=None)
    assert avisos_da_regua((item("c", 1, 3),), {"c": c}) == []  # "não sei": a classe não aparece; cobertura_solo não é mostrada


def test_alerta_do_aviso_tira_o_atencao_do_inicio_com_ou_sem_pontuacao():
    for aviso in ("Atenção: a variedade intoxica.", "Atenção, a variedade intoxica.", "Atenção a variedade intoxica."):
        c = cultura("c", avisos={"valor_forrageiro": aviso}, valor_forrageiro="alto")
        assert avisos_da_regua((item("c", 1, 3),), {"c": c})[0].texto == "C: a variedade intoxica."
    c = cultura("c", avisos={"valor_forrageiro": "A variedade intoxica."}, valor_forrageiro="alto")
    assert avisos_da_regua((item("c", 1, 3),), {"c": c})[0].texto == "C: A variedade intoxica."  # sem o prefixo, fica igual
