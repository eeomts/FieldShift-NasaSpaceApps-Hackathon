"""Graus-dia: GD = soma de max(0, Tmed - Tb), sem teto, a mesma conta de data/catalogo/scripts/gd_nasa_power.py."""
import calendar
from collections.abc import Iterable

TB_MIN = 0  # Tb inteiras gravadas por mês, de 0 a 20 °C
TB_MAX = 20


def tmed_do_dia(tmax: float | None, tmin: float | None) -> float | None:
    """Tmed = (Tmax + Tmin) / 2, como no dataset (não é o T2M do POWER). Falta um dos dois: None."""
    return None if tmax is None or tmin is None else (tmax + tmin) / 2


def graus_dia(tmed_diaria: Iterable[float | None], tb: float) -> float:
    """Soma de max(0, Tmed - Tb) sobre as temperaturas médias diárias, sem teto. Dia sem dado (None) não entra."""
    return sum(max(0.0, t - tb) for t in tmed_diaria if t is not None)


def gd_mensal_por_tb(tmed_diaria: Iterable[float | None], ano: int, mes: int) -> dict[str, float]:
    """GD do mês para cada Tb inteira de 0 a 20 (chaves "0".."20").

    Mês com algum dia sem temperatura devolve {} (completo ou nada, como o script, que descarta o ano): a soma
    parcial pareceria um mês frio. Fica diferente de NULL, que marca célula baixada antes desta coluna.
    """
    dias = list(tmed_diaria)
    if len(dias) != calendar.monthrange(ano, mes)[1] or any(t is None for t in dias):
        return {}
    return {str(tb): round(graus_dia(dias, tb), 2) for tb in range(TB_MIN, TB_MAX + 1)}


def gd_para_tb(gd_por_tb: dict[str, float] | None, tb: float) -> float | None:
    """GD de um mês para qualquer Tb entre 0 e 20.

    Tb inteira: valor gravado. Tb fracionária (ex. 11,5): interpolação linear entre as duas inteiras vizinhas.
    A curva GD(Tb) é convexa, então a corda superestima um pouco (no máximo 0,25 °C·dia por dia de dado).
    Fora de 0-20, sem o mês ou mês vazio: None (nunca inventa).
    """
    if not gd_por_tb or not (TB_MIN <= tb <= TB_MAX):
        return None
    baixo = int(tb // 1)
    alto = min(baixo + 1, TB_MAX)
    v0, v1 = gd_por_tb.get(str(baixo)), gd_por_tb.get(str(alto))
    if v0 is None or v1 is None:
        return None
    return v0 + (v1 - v0) * (tb - baixo)
