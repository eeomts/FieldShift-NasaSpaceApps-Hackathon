"""Evapotranspiração de referência diária, FAO-56 Penman-Monteith (FAO Irrigation and Drainage Paper 56)."""
import math
from datetime import date

GSC = 0.0820  # constante solar, MJ/m²/min
SIGMA = 4.903e-9  # Stefan-Boltzmann, MJ/K⁴/m²/dia


def pressao_vapor_saturacao(t_c: float) -> float:
    """e°(T) em kPa (eq. 11)."""
    return 0.6108 * math.exp(17.27 * t_c / (t_c + 237.3))


def radiacao_extraterrestre(lat: float, dia_do_ano: int) -> float:
    """Ra em MJ/m²/dia (eqs. 21 a 25)."""
    phi = math.radians(lat)
    dr = 1 + 0.033 * math.cos(2 * math.pi * dia_do_ano / 365)
    delta = 0.409 * math.sin(2 * math.pi * dia_do_ano / 365 - 1.39)
    # Em latitudes polares o sol pode não nascer ou não se pôr: limita o argumento do arco cosseno.
    x = max(-1.0, min(1.0, -math.tan(phi) * math.tan(delta)))
    ws = math.acos(x)
    return (24 * 60 / math.pi) * GSC * dr * (
        ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws)
    )


def et0_fao56(
    tmax: float, tmin: float, ea: float, u2: float, rs: float, lat: float, dia_do_ano: int, elevacao_m: float
) -> float | None:
    """ET0 em mm/dia. ea = pressão real de vapor (kPa), u2 = vento a 2 m (m/s), rs = radiação solar (MJ/m²/dia), G = 0.

    Devolve None se a radiação de céu claro (Rso) não for positiva (sol não nasce no dia).
    """
    tmed = (tmax + tmin) / 2
    es = (pressao_vapor_saturacao(tmax) + pressao_vapor_saturacao(tmin)) / 2

    delta = 4098 * pressao_vapor_saturacao(tmed) / (tmed + 237.3) ** 2
    pressao = 101.3 * ((293 - 0.0065 * elevacao_m) / 293) ** 5.26
    gama = 0.000665 * pressao

    ra = radiacao_extraterrestre(lat, dia_do_ano)
    rso = (0.75 + 2e-5 * elevacao_m) * ra
    if rso <= 0:
        return None
    rns = (1 - 0.23) * rs
    razao = max(0.3, min(1.0, rs / rso))  # a FAO limita Rs/Rso a 0,3–1,0
    rnl = SIGMA * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.0))) * (
        1.35 * razao - 0.35
    )
    rn = rns - rnl

    et0 = (0.408 * delta * rn + gama * 900 / (tmed + 273) * u2 * (es - ea)) / (delta + gama * (1 + 0.34 * u2))
    return max(0.0, et0)


def et0_diaria(
    dia: date,
    tmax: float | None,
    tmin: float | None,
    ur_pct: float | None,
    vento_2m: float | None,
    rad_mj: float | None,
    lat: float,
    elevacao_m: float | None,
) -> float | None:
    """ET0 do dia a partir dos dados do POWER; qualquer entrada ausente resulta em None (nunca um valor inventado)."""
    if None in (tmax, tmin, ur_pct, vento_2m, rad_mj, elevacao_m):
        return None
    es = (pressao_vapor_saturacao(tmax) + pressao_vapor_saturacao(tmin)) / 2
    ea = min(max(ur_pct, 0.0), 100.0) / 100 * es  # UR média do dia aplicada à média de e°(Tmax) e e°(Tmin)
    return et0_fao56(tmax, tmin, ea, vento_2m, rad_mj, lat, dia.timetuple().tm_yday, elevacao_m)
