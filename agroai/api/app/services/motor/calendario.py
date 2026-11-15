"""Meses de um período, janela vazia e divisão do ciclo em terços (meses inteiros, 1 a 12)."""
import math
from calendar import monthrange

from app.services.motor.parametros import DIAS_POR_MES


def dia_do_ano(mm_dd: str) -> int:
    """Posição do dia "MM-DD" no ano (1 a 365; o ano não tem 29/02). ValueError se o texto não for uma data."""
    mes, dia = (int(x) for x in mm_dd.split("-"))
    if not (1 <= mes <= 12 and 1 <= dia <= monthrange(2001, mes)[1]):
        raise ValueError(f"data fora do calendário: {mm_dd!r}")
    return sum(monthrange(2001, m)[1] for m in range(1, mes)) + dia


def meses_do_periodo(inicio: int | None, fim: int | None, perene: bool) -> list[int]:
    """Meses em ordem, de `inicio` a `fim` (passa de dezembro para janeiro). Perene: o ano todo. Sem mês: vazio."""
    if perene:
        return list(range(1, 13))
    if inicio is None or fim is None:
        return []
    n = (fim - inicio) % 12 + 1
    return [(inicio - 1 + i) % 12 + 1 for i in range(n)]


def maior_janela_vazia(vazios: list[int]) -> tuple[int, int] | None:
    """(mês de início, nº de meses) da maior sequência contínua de meses vazios, contando de dezembro a janeiro."""
    conjunto = set(vazios)
    if not conjunto:
        return None
    if len(conjunto) == 12:
        return 1, 12
    melhor: tuple[int, int] | None = None
    for m in sorted(conjunto):
        if (m - 2) % 12 + 1 in conjunto:
            continue  # não é começo de sequência
        n = 0
        while (m - 1 + n) % 12 + 1 in conjunto:
            n += 1
        if melhor is None or n > melhor[1]:
            melhor = (m, n)
    return melhor


def meses_para_dias(n_meses: int) -> float:
    return n_meses * DIAS_POR_MES


def meses_necessarios(ciclo_dias: float) -> int:
    """Menor nº de meses inteiros que cobre o ciclo."""
    return max(1, math.ceil(ciclo_dias / DIAS_POR_MES - 1e-9))


def meses_do_terco_medio(meses: list[int]) -> list[int]:
    """Meses inteiros do período que tocam o terço do meio do ciclo (a floração, quando o Kc é médio)."""
    partes = partes_por_terco(len(meses))
    return [m for m, p in zip(meses, partes) if any(t == 1 for t, _ in p)]


def partes_por_terco(n_meses: int) -> list[list[tuple[int, float]]]:
    """Para cada mês do período (índice 0..n-1): [(terço 0..2, fração do mês nesse terço)]. As frações do mês somam 1."""
    saida = []
    for i in range(n_meses):
        lo, hi = i / n_meses, (i + 1) / n_meses
        partes = []
        for t in range(3):
            sobra = min(hi, (t + 1) / 3) - max(lo, t / 3)
            if sobra > 1e-12:
                partes.append((t, sobra * n_meses))
        saida.append(partes)
    return saida
