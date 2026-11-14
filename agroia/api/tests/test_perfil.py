from app.onboarding.perfil import calcula_perfil, meses_sem_cobertura
from app.onboarding.schemas import ItemCalendario, Respostas


def test_regras_do_perfil():
    assert calcula_perfil(Respostas(q1_quem="tecnico", q12_analise="sim", q12_tem_resultado="sim")) == "D"
    assert calcula_perfil(Respostas(q12_analise="sim", q12_tem_resultado="sim")) == "C"
    assert calcula_perfil(Respostas(q12_analise="sim", q12_tem_resultado="nao")) == "A"
    assert calcula_perfil(Respostas(q13_textura="argilosa")) == "B"
    cinco = dict(q14_encharca="nao", q15_casca="sim", q16_erosao="sim", q17_dura="nao", q18_minhocas="sim")
    assert calcula_perfil(Respostas(**cinco)) == "B"
    assert calcula_perfil(Respostas(**(cinco | {"q18_minhocas": "nao_sei"}))) == "A"
    # cor + jeito da pergunta 19 contam como uma observação
    quatro_mais_figuras = (cinco | {"q18_minhocas": "nao_sei"}) | dict(q19_cor="vermelha", q19_jeito="gruda")
    assert calcula_perfil(Respostas(**quatro_mais_figuras)) == "B"
    assert calcula_perfil(Respostas()) == "A"


def test_perguntas_de_manejo_nao_contam_como_conhecimento_do_solo():
    # 3 observações + 3 respostas de manejo ("nunca fiz análise", "nunca usei calcário", "não uso adubo")
    manejo = dict(q12_analise="nao", q21_calcario="nao", q22_adubo="nao",
                  q14_encharca="sim", q15_casca="nao", q16_erosao="sim")
    assert calcula_perfil(Respostas(**manejo)) == "A"


def test_meses_sem_cobertura_com_virada_de_ano_e_perene():
    soja = ItemCalendario(cultura_id="soja", texto_original="soja", inicio_mes=11, fim_mes=3)
    assert meses_sem_cobertura([soja]) == [4, 5, 6, 7, 8, 9, 10]
    capim = ItemCalendario(cultura_id="pastagem", texto_original="capim", perene=True)
    assert meses_sem_cobertura([soja, capim]) == []
    assert meses_sem_cobertura([]) == []
