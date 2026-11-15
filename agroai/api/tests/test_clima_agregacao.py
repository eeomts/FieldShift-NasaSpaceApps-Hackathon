"""Agregação mensal com séries sintéticas: valor ausente nunca vira 0."""
from datetime import date, timedelta

import pytest

from app.services.clima.agregacao import DiaClima, agregar_por_mes, limite_chuva_forte, percentil, series_por_ano


def dia(data: date, tmax=30.0, tmin=15.0, chuva=0.0, et0=4.0) -> DiaClima:
    tmed = None if tmax is None or tmin is None else (tmax + tmin) / 2
    return DiaClima(data=data, tmed=tmed, tmax=tmax, tmin=tmin, chuva=chuva, et0=et0)


def mes(ano: int, m: int, n: int, **kw) -> list[DiaClima]:
    return [dia(date(ano, m, d), **kw) for d in range(1, n + 1)]


def test_percentil_interpola_como_o_numpy():
    assert percentil([1, 2, 3, 4], 50) == 2.5
    assert percentil(list(range(1, 102)), 95) == 96.0
    assert percentil([], 95) is None


def test_somas_e_medias_do_mes():
    [l] = agregar_por_mes(mes(2000, 1, 31, chuva=2.0, et0=5.0), limite_forte=None)
    assert (l.ano, l.mes) == (2000, 1)
    assert l.chuva_mm == 62.0
    assert l.et0_mm == 155.0
    assert l.tmed_c == 22.5
    assert l.tmax_media_c == 30.0
    assert l.tmin_media_c == 15.0
    assert l.dias_validos == 31


def test_valor_ausente_nao_entra_na_conta_nem_vira_zero():
    dias = mes(2000, 1, 4, chuva=10.0)
    dias[1] = dia(date(2000, 1, 2), tmax=None, tmin=None, chuva=None, et0=None)
    [l] = agregar_por_mes(dias, limite_forte=None)
    assert l.chuva_mm == 30.0  # 3 dias com dado
    assert l.tmax_media_c == 30.0
    assert l.dias_validos == 3


def test_mes_sem_nenhum_dado_vira_none():
    dias = [dia(date(2000, 2, d), tmax=None, tmin=None, chuva=None, et0=None) for d in range(1, 29)]
    [l] = agregar_por_mes(dias, limite_forte=25.0)
    for campo in (
        "chuva_mm", "et0_mm", "tmed_c", "tmax_media_c", "tmin_media_c", "tmax_absoluta_c", "tmin_absoluta_c",
        "dias_geada", "dias_calor", "dias_chuva_forte", "maior_seq_seca_dias",
    ):  # fmt: skip
        assert getattr(l, campo) is None, campo
    assert l.dias_validos == 0


def test_geada_e_tmin_abaixo_de_2_graus():
    dias = mes(2000, 7, 6, tmin=10.0)
    for d, t in zip(dias[:3], (1.9, 2.0, -1.0)):  # 2,0 não é geada
        d.tmin = t
    [l] = agregar_por_mes(dias, limite_forte=None)
    assert l.dias_geada == 2
    assert l.tmin_absoluta_c == -1.0


def test_calor_e_tmax_acima_de_35_graus():
    dias = mes(2000, 1, 5)
    for d, t in zip(dias, (35.0, 35.1, 40.2)):  # 35,0 não é calor
        d.tmax = t
    [l] = agregar_por_mes(dias, limite_forte=None)
    assert l.dias_calor == 2
    assert l.tmax_absoluta_c == 40.2


def test_chuva_forte_e_maior_que_o_limite():
    dias = mes(2000, 1, 5)
    for d, c in zip(dias, (24.9, 25.0, 25.1, 80.0)):
        d.chuva = c
    [l] = agregar_por_mes(dias, limite_forte=25.0)
    assert l.dias_chuva_forte == 2


def test_chuva_forte_sem_limite_e_none():
    [l] = agregar_por_mes(mes(2000, 1, 5, chuva=50.0), limite_forte=None)
    assert l.dias_chuva_forte is None


def test_limite_chuva_forte_so_conta_dias_com_chuva_do_periodo_base():
    dias = []
    inicio = date(1991, 1, 1)
    for i in range(1000):
        d = inicio + timedelta(days=i)
        dias.append(dia(d, chuva=0.5 if i % 2 else 1.0 + (i % 100) / 10))  # 0,5 mm não conta como dia com chuva
    dias.append(dia(date(2023, 1, 1), chuva=500.0))  # fora de 1991-2020: não conta
    limite = limite_chuva_forte(dias)
    chuvas = sorted(1.0 + (i % 100) / 10 for i in range(0, 1000, 2))
    assert limite == pytest.approx(percentil(chuvas, 95), abs=0.01)
    assert limite < 15


def test_limite_chuva_forte_com_poucos_dias_e_none():
    assert limite_chuva_forte(mes(2000, 1, 31, chuva=5.0)) is None


def test_maior_sequencia_seca_dentro_do_mes():
    chuvas = [0, 0, 0, 5, 0.5, 0, 0, 0, 0, 3, 0]  # secos < 1 mm: 3, depois 0,5+0+0+0+0 = 5, depois 1
    dias = [dia(date(2000, 3, i + 1), chuva=c) for i, c in enumerate(chuvas)]
    [l] = agregar_por_mes(dias, limite_forte=None)
    assert l.maior_seq_seca_dias == 5


def test_chuva_de_1mm_quebra_a_sequencia_seca():
    chuvas = [0, 0, 1.0, 0, 0, 0]
    dias = [dia(date(2000, 3, i + 1), chuva=c) for i, c in enumerate(chuvas)]
    [l] = agregar_por_mes(dias, limite_forte=None)
    assert l.maior_seq_seca_dias == 3


def test_sequencia_seca_nao_atravessa_o_mes_nem_dia_sem_dado():
    dias = mes(2000, 3, 31, chuva=0.0)[-3:] + mes(2000, 4, 2, chuva=0.0)
    linhas = agregar_por_mes(dias, limite_forte=None)
    assert [l.maior_seq_seca_dias for l in linhas] == [3, 2]
    dias = mes(2000, 5, 3, chuva=0.0)
    dias[1].chuva = None  # dia sem dado interrompe
    [l] = agregar_por_mes(dias, limite_forte=None)
    assert l.maior_seq_seca_dias == 1


def test_meses_saem_em_ordem_cronologica():
    dias = mes(2001, 1, 2) + mes(2000, 12, 2) + mes(2000, 2, 2)
    assert [(l.ano, l.mes) for l in agregar_por_mes(dias, limite_forte=None)] == [(2000, 2), (2000, 12), (2001, 1)]


def test_series_por_ano_indice_zero_e_1_de_janeiro_e_bissexto_tem_366():
    dias = [dia(date(2023, 1, 1) + timedelta(days=i), tmax=30.0 + i % 3, tmin=10.0 + i % 3) for i in range(365 + 366)]  # 2023 e 2024
    s23, s24 = series_por_ano(dias)
    assert (s23.ano, s24.ano) == (2023, 2024) and len(s23.tmin_c) == 365 and len(s24.tmax_c) == 366
    assert s23.tmin_c[0] == 10.0 and s23.tmax_c[1] == 31.0 and s24.tmin_c[59] == dias[365 + 59].tmin  # 29 de fevereiro de 2024


def test_series_por_ano_dia_sem_dado_ou_ausente_na_serie_fica_none_nunca_zero():
    dias = [dia(date(2023, 1, 1), tmin=None), dia(date(2023, 1, 3), tmax=None)]  # 2 de janeiro nem veio
    (s,) = series_por_ano(dias)
    assert s.tmin_c[:3] == [None, None, 15.0] and s.tmax_c[:3] == [30.0, None, None]
    assert 0 not in s.tmin_c and 0 not in s.tmax_c and len(s.tmin_c) == 365
