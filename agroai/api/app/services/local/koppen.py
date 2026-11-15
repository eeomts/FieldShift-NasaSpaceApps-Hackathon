"""Zona climática de Köppen-Geiger a partir da climatologia mensal (temperatura e chuva).

O yaml do questionário cita o mapa de 1 km de Beck et al. (2023). Não temos esse raster, então esta é uma
APROXIMAÇÃO: aplica as regras do Köppen-Geiger (como em Beck et al.) à climatologia do NASA POWER, em
células de ~50 km. Perto de fronteiras entre zonas ou em relevo forte, a classe pode diferir do mapa de 1 km.
"""

DIAS_DO_MES = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
_VERAO = {"N": {4, 5, 6, 7, 8, 9}, "S": {10, 11, 12, 1, 2, 3}}


def chuva_mensal_mm(mm_por_dia: list[float]) -> list[float]:
    """Chuva em mm/dia (como vem do POWER) -> mm no mês."""
    return [v * d for v, d in zip(mm_por_dia, DIAS_DO_MES, strict=True)]


def koppen(temp_c: list[float], chuva_mm: list[float], hemisferio: str) -> str:
    """Classe Köppen-Geiger (ex.: "Aw", "BSh", "Cfa", "Dfa") de 12 médias mensais (jan..dez).

    temp_c: temperatura média do mês em °C. chuva_mm: chuva total do mês em mm.
    """
    if len(temp_c) != 12 or len(chuva_mm) != 12:
        raise ValueError("são necessários 12 valores mensais")
    verao = _VERAO["S" if hemisferio == "S" else "N"]
    meses = range(1, 13)
    t_ano = sum(temp_c) / 12
    t_max, t_min = max(temp_c), min(temp_c)
    p_ano = sum(chuva_mm)
    p_verao = [chuva_mm[m - 1] for m in meses if m in verao]
    p_inverno = [chuva_mm[m - 1] for m in meses if m not in verao]

    # E: polar
    if t_max < 10:
        return "ET" if t_max > 0 else "EF"

    # B: seco. O limiar sobe quando a chuva cai no verão e desce quando cai no inverno.
    fracao_verao = sum(p_verao) / p_ano if p_ano > 0 else 0.5
    if fracao_verao >= 0.7:
        limiar = 20 * t_ano + 280
    elif fracao_verao <= 0.3:
        limiar = 20 * t_ano
    else:
        limiar = 20 * t_ano + 140
    if p_ano < limiar:
        deserto = "W" if p_ano < limiar / 2 else "S"
        return f"B{deserto}{'h' if t_ano >= 18 else 'k'}"

    mes_mais_seco = min(chuva_mm)
    # A: tropical
    if t_min >= 18:
        if mes_mais_seco >= 60:
            return "Af"
        if mes_mais_seco >= 100 - p_ano / 25:
            return "Am"
        return "As" if (chuva_mm.index(mes_mais_seco) + 1) in verao else "Aw"

    # C (temperado) ou D (frio)
    grupo = "C" if t_min > -3 else "D"
    seco_verao, umido_verao = min(p_verao), max(p_verao)
    seco_inverno, umido_inverno = min(p_inverno), max(p_inverno)
    if seco_verao < 40 and seco_verao < umido_inverno / 3:
        sazonal = "s"
    elif seco_inverno < umido_verao / 10:
        sazonal = "w"
    else:
        sazonal = "f"
    if t_max >= 22:
        verao_q = "a"
    elif sum(t >= 10 for t in temp_c) >= 4:
        verao_q = "b"
    elif grupo == "D" and t_min <= -38:
        verao_q = "d"
    else:
        verao_q = "c"
    return f"{grupo}{sazonal}{verao_q}"
