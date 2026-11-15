"""Derivados do solo: classe textural (Embrapa), matéria orgânica, acidez (faixas do laudo) e K da USLE (Williams)."""
import pytest

from app.schemas.onboarding import Respostas
from app.services.onboarding.perfil import retrato_solo
from app.services.solo.derivados import (
    classe_acidez,
    classe_materia_organica,
    classe_textural,
    erodibilidade_k,
    materia_organica_g_kg,
    textura_simples,
)


@pytest.mark.parametrize(
    "argila,areia,silte,classe",
    [
        (70, 20, 10, "muito_argilosa"),  # acima de 60 % de argila
        (60, 25, 15, "argilosa"),  # 60 ainda é argilosa
        (35, 40, 25, "argilosa"),  # de 35 a 60
        (40, 40, 20, "argilosa"),
        (25, 35, 40, "media"),  # menos de 35 % de argila e mais de 15 % de areia
        (34.9, 30, 35.1, "media"),
        (10, 10, 80, "siltosa"),  # menos de 35 % de argila e menos de 15 % de areia
        (5, 90, 5, "arenosa"),  # silte + 2·argila < 30 (areia)
        (10, 80, 5, "arenosa"),  # areia franca
        (10, 80, 10, "media"),  # silte + 2·argila = 30: já é franco-arenosa
    ],
)
def test_classe_textural_da_embrapa(argila, areia, silte, classe):
    assert classe_textural(argila, areia, silte) == classe


def test_classe_textural_sem_um_dos_tres_e_none():
    assert classe_textural(None, 40, 20) is None
    assert classe_textural(40, None, 20) is None
    assert classe_textural(40, 40, None) is None


def test_textura_simples_agrupa_nas_tres_do_questionario():
    classes = ("arenosa", "media", "argilosa", "muito_argilosa", "siltosa", None)
    assert [textura_simples(c) for c in classes] == ["arenosa", "media", "argilosa", "argilosa", "media", None]


def test_materia_organica_e_carbono_vezes_1_724():
    assert materia_organica_g_kg(20.0) == pytest.approx(34.48)
    assert materia_organica_g_kg(None) is None


@pytest.mark.parametrize("ph,classe", [(4.9, "alta"), (5.0, "media"), (5.9, "media"), (6.0, "adequada"), (6.9, "adequada"), (7.0, "alcalino"), (None, None)])
def test_acidez_pelas_faixas_do_laudo(ph, classe):
    assert classe_acidez(ph) == classe


def test_acidez_do_mapa_e_do_laudo_dao_a_mesma_classe():
    # as faixas vêm de perfil.py: o mesmo pH não pode dar classes diferentes no laudo e no mapa
    for ph in (4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0):
        do_laudo = retrato_solo(Respostas(q12_analise="sim", q12_tem_resultado="sim", q12_laudo={"ph_agua": ph, "argila_pct": 30}))
        classe_laudo = next(i["valor"] for i in do_laudo["indicadores"] if i["atributo"] == "acidez")
        assert classe_acidez(ph) == classe_laudo


def test_materia_organica_usa_as_faixas_do_laudo_em_g_dm3():
    assert classe_materia_organica(15.0) == "baixa"  # < 20
    assert classe_materia_organica(30.0) == "media"
    assert classe_materia_organica(45.0) == "alta"
    # g/kg × densidade = g/dm³: 25 g/kg × 0,7 = 17,5 g/dm³ (baixa); 25 × 1,2 = 30 (média)
    assert classe_materia_organica(25.0, 0.7) == "baixa"
    assert classe_materia_organica(25.0, 1.2) == "media"
    assert classe_materia_organica(None) is None


def test_k_usle_a_mao():
    # areia 40 %, silte 20 %, argila 40 %, carbono 2 % (20 g/kg):
    # f_csand = 0,2 + 0,3·exp(−0,256·40·0,8) = 0,20008; f_cl-si = (20/60)^0,3 = 0,71933
    # f_orgC = 1 − 0,25·2/(2 + exp(3,72 − 2,95·2)) = 0,76336; f_hisand = 1 − 0,7·0,6/(0,6 + exp(−5,51 + 22,9·0,6)) = 0,99989
    # K americano = 0,10985; × 0,1317 = 0,01447 t·ha·h/(ha·MJ·mm)
    assert erodibilidade_k(argila_pct=40, areia_pct=40, silte_pct=20, carbono_g_kg=20) == pytest.approx(0.0145, abs=1e-4)


def test_k_cresce_com_o_silte_e_cai_com_o_carbono():
    argiloso = erodibilidade_k(60, 20, 20, 10)
    siltoso = erodibilidade_k(20, 10, 70, 10)
    assert siltoso > 2 * argiloso
    assert erodibilidade_k(20, 10, 70, 30) < siltoso  # mais carbono, menos erodível


def test_k_sem_dado_ou_sem_argila_e_silte_e_none():
    assert erodibilidade_k(None, 40, 20, 20) is None
    assert erodibilidade_k(40, 40, 20, None) is None
    assert erodibilidade_k(0, 100, 0, 5) is None
