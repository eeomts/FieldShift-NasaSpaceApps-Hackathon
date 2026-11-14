from app.onboarding.perfil import calcula_perfil, meses_sem_cobertura
from app.onboarding.schemas import ItemCalendario, Respostas


def test_regras_do_perfil():
    assert calcula_perfil(Respostas(q1_quem="tecnico", q12_analise="sim", q12_tem_resultado="sim")) == "D"
    assert calcula_perfil(Respostas(q12_analise="sim", q12_tem_resultado="sim")) == "C"
    assert calcula_perfil(Respostas(q12_analise="sim", q12_tem_resultado="nao")) == "A"
    assert calcula_perfil(Respostas(q13_textura="argilosa")) == "B"
    seis = dict(q14_encharca="nao", q15_casca="sim", q16_erosao="sim", q17_dura="nao", q18_minhocas="sim", q21_calcario="sim")
    assert calcula_perfil(Respostas(**seis)) == "B"
    assert calcula_perfil(Respostas(**(seis | {"q21_calcario": "nao_sei"}))) == "A"
    assert calcula_perfil(Respostas()) == "A"


def test_meses_sem_cobertura_com_virada_de_ano_e_perene():
    soja = ItemCalendario(cultura_id="soja", texto_original="soja", inicio_mes=11, fim_mes=3)
    assert meses_sem_cobertura([soja]) == [4, 5, 6, 7, 8, 9, 10]
    capim = ItemCalendario(cultura_id="pastagem", texto_original="capim", perene=True)
    assert meses_sem_cobertura([soja, capim]) == []
    assert meses_sem_cobertura([]) == []
