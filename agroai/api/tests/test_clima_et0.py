"""ET0 FAO-56: exemplo oficial (Example 18, Bruxelas, 6 de julho) e entradas ausentes."""
from datetime import date

import pytest

from app.services.clima.et0 import et0_diaria, et0_fao56, radiacao_extraterrestre


def test_ra_do_exemplo_da_fao():
    assert radiacao_extraterrestre(50.8, 187) == pytest.approx(41.1, abs=0.2)  # FAO: 41,09


def test_et0_exemplo_18_da_fao():
    # Tmax 21,5; Tmin 12,3; ea 1,409 kPa; u2 2,078 m/s; Rs 22,07 MJ/m²/dia; 50°48'N; 100 m; dia 187
    et0 = et0_fao56(tmax=21.5, tmin=12.3, ea=1.409, u2=2.078, rs=22.07, lat=50.8, dia_do_ano=187, elevacao_m=100)
    assert et0 == pytest.approx(3.9, abs=0.1)


def test_et0_diaria_com_umidade_relativa_fica_perto_do_exemplo():
    # UR média 73,5% sobre es = 2,064 kPa dá ea ~1,52 kPa (a FAO usa UR máx e mín, então a tolerância é maior)
    et0 = et0_diaria(date(2001, 7, 6), 21.5, 12.3, 73.5, 2.078, 22.07, 50.8, 100)
    assert 3.4 <= et0 <= 4.2


@pytest.mark.parametrize("faltando", range(6))
def test_et0_diaria_com_entrada_ausente_e_none(faltando):
    entradas = [21.5, 12.3, 73.5, 2.078, 22.07, 100.0]
    entradas[faltando] = None
    tmax, tmin, ur, vento, rad, elev = entradas
    assert et0_diaria(date(2001, 7, 6), tmax, tmin, ur, vento, rad, 50.8, elev) is None


def test_et0_nunca_e_negativa():
    assert et0_fao56(tmax=2.0, tmin=-3.0, ea=0.5, u2=0.5, rs=1.0, lat=60.0, dia_do_ano=355, elevacao_m=0) >= 0


def test_noite_polar_devolve_none_em_vez_de_inventar():
    assert et0_fao56(tmax=-5.0, tmin=-15.0, ea=0.2, u2=2.0, rs=0.0, lat=89.0, dia_do_ano=355, elevacao_m=0) is None
