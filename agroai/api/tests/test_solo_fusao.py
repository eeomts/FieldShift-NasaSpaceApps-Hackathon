"""Fusão de evidências do solo: pesos por fonte, confiança, divergência com o mapa global e o laudo que decide."""
import pytest

from app.schemas.onboarding import Respostas
from app.schemas.solo import SoloPonto
from app.services.onboarding.perfil import retrato_solo
from app.services.solo import fusao
from app.services.solo.retrato import montar_retrato
from app.services.solo.solo_service import ponto_da_camada
from solo_helpers import amostra, camada, resposta


def mapa(argila=40, areia=40, silte=20, carbono=20.0, ph=5.5, densidade=1.2) -> SoloPonto:
    """Ponto do mapa global com os números dados (classe textural, matéria orgânica e K derivados como no serviço)."""
    corpo = resposta(
        camada("clay", [argila * 10] * 5), camada("sand", [areia * 10] * 5), camada("silt", [silte * 10] * 5),
        camada("soc", [int(carbono * 10)] * 5), camada("phh2o", [int(ph * 10)] * 5), camada("bdod", [int(densidade * 100)] * 5),
    )  # fmt: skip
    return ponto_da_camada(amostra(corpo).superficial)


def sintese(respostas: Respostas, solo: SoloPonto | None) -> dict[str, dict]:
    return {a.atributo: a.model_dump() for a in fusao.sintese(retrato_solo(respostas), solo)}


ARGILOSO = mapa(argila=45, areia=35, silte=20)
ARENOSO = mapa(argila=8, areia=85, silte=7)


def test_pesos_por_fonte():
    assert fusao.PESO_POR_FONTE == {"laudo": 0.9, "teste_campo": 0.7, "produtor": 0.5, "soilgrids": 0.4}


def test_so_o_mapa_da_confianca_baixa_e_sem_divergencia():
    t = sintese(Respostas(), ARGILOSO)["textura"]
    assert t["valor"] == "argilosa" and t["confianca"] == "baixa" and t["divergencia"] is None
    assert [(e["fonte"], e["peso"]) for e in t["evidencias"]] == [("soilgrids", 0.4)]
    assert "45% de argila" in t["evidencias"][0]["texto"]


def test_produtor_e_mapa_concordam_confianca_alta():
    t = sintese(Respostas(q13_textura="argilosa"), ARGILOSO)["textura"]
    assert t["valor"] == "argilosa" and t["confianca"] == "alta" and t["divergencia"] is None
    assert [e["fonte"] for e in t["evidencias"]] == ["produtor", "soilgrids"]


def test_so_o_produtor_da_confianca_media():
    t = sintese(Respostas(q13_textura="media"), None)["textura"]
    assert (t["valor"], t["confianca"]) == ("media", "media")


def test_divergencia_o_produtor_vence_e_a_frase_aparece():
    t = sintese(Respostas(q13_textura="arenosa"), ARGILOSO)["textura"]
    assert t["valor"] == "arenosa"  # 0,5 contra 0,4
    assert t["confianca"] == "media"  # há discordância
    assert t["divergencia"] == "O mapa global sugere terra argilosa, mas você observou terra arenosa. No seu campo vale o que você vê."


def test_exemplo_da_drenagem_do_motor_votos_somados():
    # figuras: jeito "solta" = arenosa; pergunta 13 = arenosa; mapa = argilosa (1,0 contra 0,4)
    t = sintese(Respostas(q13_textura="arenosa", q19_cor="clara", q19_jeito="solta"), ARGILOSO)["textura"]
    assert t["valor"] == "arenosa" and t["confianca"] == "media"
    assert sum(e["peso"] for e in t["evidencias"] if e["valor"] == "arenosa") == pytest.approx(1.0)
    assert t["divergencia"] is not None


def test_nao_sei_nao_gera_evidencia():
    s = sintese(Respostas(q13_textura="nao_sei", q19_cor="nao_sei", q19_jeito="nao_sei"), None)
    assert all(a["valor"] is None and a["confianca"] is None and a["evidencias"] == [] for a in s.values())
    t = sintese(Respostas(q13_textura="nao_sei"), ARGILOSO)["textura"]
    assert [e["fonte"] for e in t["evidencias"]] == ["soilgrids"]  # só o mapa
    assert t["divergencia"] is None


def test_laudo_vence_mesmo_contra_o_produtor_e_o_mapa():
    r = Respostas(q12_analise="sim", q12_tem_resultado="sim", q12_laudo={"argila_pct": 10, "ph_agua": 5.5},
                  q13_textura="argilosa", q19_cor="vermelha", q19_jeito="gruda")  # fmt: skip
    t = sintese(r, ARGILOSO)["textura"]
    assert t["valor"] == "arenosa" and t["confianca"] == "alta"  # o laudo (argila 10 %) decide; 1,0 + 0,4 de votos contrários não pesam
    assert t["evidencias"][0]["fonte"] == "laudo" and t["evidencias"][0]["peso"] == 0.9
    assert t["divergencia"] is None  # a frase é só do mapa contra o que o produtor viu


def test_laudo_e_mapa_do_acidez_e_o_mapa_do_resto():
    r = Respostas(q12_analise="sim", q12_tem_resultado="sim", q12_laudo={"ph_agua": 4.6, "argila_pct": 30})
    s = sintese(r, mapa(ph=6.4))
    assert s["acidez"]["valor"] == "alta" and s["acidez"]["confianca"] == "alta"
    assert s["materia_organica"]["evidencias"][0]["fonte"] == "soilgrids"  # sem laudo de MO: só o mapa


def test_materia_organica_pela_cor_da_terra_e_pelo_mapa():
    # carbono 2 % → MO 34,5 g/kg × densidade 1,2 = 41 g/dm³ (alta); cor "clara" diz baixa
    s = sintese(Respostas(q19_cor="clara"), mapa(carbono=20.0))["materia_organica"]
    assert s["valor"] == "baixa" and s["confianca"] == "media"
    assert s["divergencia"] == "O mapa global sugere bastante matéria orgânica, mas você observou pouca matéria orgânica. No seu campo vale o que você vê."
    concordam = sintese(Respostas(q19_cor="escura"), mapa(carbono=20.0))["materia_organica"]
    assert concordam["valor"] == "alta" and concordam["confianca"] == "alta"


def test_acidez_so_vem_do_laudo_e_do_mapa():
    s = sintese(Respostas(q13_textura="media"), mapa(ph=4.8))["acidez"]
    assert s["valor"] == "alta" and s["confianca"] == "baixa"
    assert [e["fonte"] for e in s["evidencias"]] == ["soilgrids"]


def test_sem_dado_no_mapa_so_o_produtor():
    s = sintese(Respostas(q13_textura="argilosa"), SoloPonto(sem_dado=True))
    assert s["textura"]["valor"] == "argilosa" and [e["fonte"] for e in s["textura"]["evidencias"]] == ["produtor"]
    assert s["acidez"]["valor"] is None


def test_empate_fica_com_o_que_apareceu_primeiro_e_confianca_media():
    # pergunta 13 diz arenosa (0,5); o jeito "gruda" diz argilosa (0,5)
    t = sintese(Respostas(q13_textura="arenosa", q19_cor="marrom", q19_jeito="gruda"), None)["textura"]
    assert t["valor"] == "arenosa" and t["confianca"] == "media"


def test_teste_de_campo_pesa_mais_que_o_produtor():
    retrato = {"indicadores": [
        {"atributo": "textura", "valor": "arenosa", "fonte": "teste_campo", "texto": "Teste do tato: arenosa"},
        {"atributo": "textura", "valor": "argilosa", "fonte": "produtor", "texto": "Mais argilosa"},
    ]}  # fmt: skip
    t = fusao.sintese(retrato, None)[0]
    assert t.valor == "arenosa" and [e.peso for e in t.evidencias] == [0.7, 0.5]


def test_valor_desconhecido_ou_fonte_desconhecida_e_ignorado():
    retrato = {"indicadores": [
        {"atributo": "textura", "valor": "pedregosa", "fonte": "produtor", "texto": ""},
        {"atributo": "textura", "valor": "media", "fonte": "vizinho", "texto": ""},
        {"atributo": "drenagem", "valor": "ruim", "fonte": "produtor", "texto": ""},
    ]}  # fmt: skip
    assert all(a.valor is None for a in fusao.sintese(retrato, None))


def test_a_sintese_tem_sempre_os_tres_atributos_na_mesma_ordem():
    assert [a.atributo for a in fusao.sintese(retrato_solo(Respostas()), None)] == ["textura", "materia_organica", "acidez"]


def test_retrato_montado_mantem_indicadores_e_figuras_e_acrescenta_sintese_e_mapa():
    r = Respostas(q13_textura="argilosa", q14_encharca="sim", q19_cor="escura", q19_jeito="fofa")
    sem_mapa = montar_retrato(r, None)
    base = retrato_solo(r)
    assert sem_mapa["indicadores"] == base["indicadores"] and sem_mapa["figuras"] == base["figuras"] and sem_mapa["fonte"] == "produtor"
    assert sem_mapa["soilgrids"] is None and len(sem_mapa["sintese"]) == 3
    com_mapa = montar_retrato(r, ARGILOSO)
    assert com_mapa["soilgrids"]["classe_textural"] == "argilosa" and com_mapa["soilgrids"]["camada"] == "0–30 cm"
    assert com_mapa["sintese"][0]["confianca"] == "alta"
