"""Graus-dia: caso calculado à mão, sem teto, interpolação e a conta mensal."""
import pytest

from app.services.clima.graus_dia import gd_mensal_por_tb, gd_para_tb, graus_dia, tmed_do_dia


def test_graus_dia_a_mao_sem_teto():
    # Tb 10: (5 -> 0) + (10 -> 0) + (15 -> 5) + (25 -> 15) + (40 -> 30, sem teto) = 50
    assert graus_dia([5.0, 10.0, 15.0, 25.0, 40.0], 10) == 50.0
    assert graus_dia([20.0, 22.0], 11.5) == pytest.approx(8.5 + 10.5)


def test_dia_sem_dado_nao_entra_nem_vira_zero():
    assert graus_dia([None, 20.0, None], 10) == 10.0
    assert graus_dia([None, None], 10) == 0.0


def test_tmed_e_a_media_de_tmax_e_tmin_nao_o_t2m():
    assert tmed_do_dia(30.0, 14.0) == 22.0
    assert tmed_do_dia(30.0, None) is None and tmed_do_dia(None, 10.0) is None


def test_mesma_conta_do_script_gd_nasa_power():
    """Conta de gd_ano() do script do dataset: sum(max(0, (tmax + tmin) / 2 - tb))."""
    dias = [(30.0, 14.0), (18.0, 4.0), (35.0, 21.0), (9.0, -3.0)]
    tb = 10
    do_script = sum(max(0.0, (tmax + tmin) / 2 - tb) for tmax, tmin in dias)
    assert graus_dia([tmed_do_dia(a, b) for a, b in dias], tb) == do_script == 12 + 1 + 18


def test_gd_mensal_por_tb_de_0_a_20():
    gd = gd_mensal_por_tb([22.5] * 28, 2023, 2)
    assert list(gd) == [str(t) for t in range(21)]
    assert gd["0"] == 28 * 22.5 and gd["10"] == 28 * 12.5 and gd["20"] == 28 * 2.5


def test_mes_incompleto_ou_com_dia_sem_dado_fica_vazio():
    assert gd_mensal_por_tb([22.5] * 27, 2023, 2) == {}  # falta um dia
    assert gd_mensal_por_tb([22.5] * 27 + [None], 2023, 2) == {}
    assert gd_mensal_por_tb([22.5] * 29, 2024, 2)["10"] == 29 * 12.5  # ano bissexto


def test_interpolacao_linear_entre_tb_inteiras():
    gd = {str(t): float(100 - 5 * t) for t in range(21)}  # 100, 95, ..., 0
    assert gd_para_tb(gd, 10) == 50.0
    assert gd_para_tb(gd, 11.5) == pytest.approx(42.5)
    assert gd_para_tb(gd, 20) == 0.0 and gd_para_tb(gd, 0) == 100.0


def test_interpolacao_sem_dado_ou_fora_da_faixa_e_none():
    gd = {str(t): 10.0 for t in range(21)}
    assert gd_para_tb(gd, 21) is None and gd_para_tb(gd, -0.5) is None
    assert gd_para_tb({}, 10) is None and gd_para_tb(None, 10) is None
    assert gd_para_tb({"10": 1.0}, 10.5) is None  # falta o vizinho
