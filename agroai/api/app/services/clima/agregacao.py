"""Série diária -> linhas mensais (somas, médias, extremos e contagens). Dia ausente não entra na conta da variável."""
import calendar
from dataclasses import dataclass
from datetime import date, timedelta

from app.services.clima.graus_dia import gd_mensal_por_tb, tmed_do_dia
from app.services.clima.limiares import (
    BASE_FIM,
    BASE_INICIO,
    CHUVA_DIA_SECO_MM,
    PERCENTIL_CHUVA_FORTE,
    TMAX_CALOR_C,
    TMIN_GEADA_C,
)

# Menos dias com chuva que isto no período-base: o percentil não é confiável e o limite fica ausente.
MIN_DIAS_COM_CHUVA_PARA_LIMITE = 100


@dataclass
class DiaClima:
    data: date
    tmed: float | None
    tmax: float | None
    tmin: float | None
    chuva: float | None
    et0: float | None


@dataclass
class LinhaMensal:
    ano: int
    mes: int
    chuva_mm: float | None
    et0_mm: float | None
    tmed_c: float | None
    tmax_media_c: float | None
    tmin_media_c: float | None
    tmax_absoluta_c: float | None
    tmin_absoluta_c: float | None
    dias_geada: int | None
    dias_calor: int | None
    dias_chuva_forte: int | None
    maior_seq_seca_dias: int | None
    dias_validos: int
    gd_por_tb: dict[str, float] | None = None  # GD do mês por Tb inteira 0-20; {} = mês sem temperatura completa


@dataclass
class SerieDoAno:
    """Tmin e Tmax de cada dia do ano (índice 0 = 1º de janeiro; 366 valores em ano bissexto); sem dado = None."""

    ano: int
    tmin_c: list[float | None]
    tmax_c: list[float | None]


def series_por_ano(dias: list[DiaClima]) -> list[SerieDoAno]:
    """Uma série por ano presente nos dias, em ordem. Dia que falta na série fica None."""
    por_ano: dict[int, SerieDoAno] = {}
    for d in dias:
        n = 366 if calendar.isleap(d.data.year) else 365
        serie = por_ano.setdefault(d.data.year, SerieDoAno(d.data.year, [None] * n, [None] * n))
        i = d.data.timetuple().tm_yday - 1
        serie.tmin_c[i], serie.tmax_c[i] = d.tmin, d.tmax
    return [por_ano[a] for a in sorted(por_ano)]


def percentil(valores: list[float], p: float) -> float | None:
    """Percentil por interpolação linear entre os vizinhos (mesmo método padrão do numpy)."""
    if not valores:
        return None
    v = sorted(valores)
    pos = (len(v) - 1) * p / 100
    baixo = int(pos)
    alto = min(baixo + 1, len(v) - 1)
    return v[baixo] + (v[alto] - v[baixo]) * (pos - baixo)


def limite_chuva_forte(dias: list[DiaClima]) -> float | None:
    """Percentil 95 da chuva dos dias com chuva (>= 1 mm) em 1991-2020; None se faltar dado para calcular."""
    chuvas = [
        d.chuva
        for d in dias
        if d.chuva is not None and d.chuva >= CHUVA_DIA_SECO_MM and BASE_INICIO <= d.data.year <= BASE_FIM
    ]
    if len(chuvas) < MIN_DIAS_COM_CHUVA_PARA_LIMITE:
        return None
    return round(percentil(chuvas, PERCENTIL_CHUVA_FORTE), 2)


def _soma(valores: list[float]) -> float | None:
    return round(sum(valores), 2) if valores else None


def _media(valores: list[float]) -> float | None:
    return round(sum(valores) / len(valores), 2) if valores else None


def _maior_sequencia_seca(dias: list[DiaClima]) -> int | None:
    """Maior sequência de dias seguidos com chuva < 1 mm dentro do mês. Dia sem dado interrompe a sequência."""
    if not any(d.chuva is not None for d in dias):
        return None
    maior = atual = 0
    anterior: date | None = None
    for d in sorted(dias, key=lambda x: x.data):
        seco = d.chuva is not None and d.chuva < CHUVA_DIA_SECO_MM
        if seco and atual and anterior is not None and d.data - anterior == timedelta(days=1):
            atual += 1
        elif seco:
            atual = 1
        else:
            atual = 0
        anterior = d.data
        maior = max(maior, atual)
    return maior


def _linha_do_mes(ano: int, mes: int, dias: list[DiaClima], limite_forte: float | None, tmax_calor: float) -> LinhaMensal:
    chuvas = [d.chuva for d in dias if d.chuva is not None]
    tmaxs = [d.tmax for d in dias if d.tmax is not None]
    tmins = [d.tmin for d in dias if d.tmin is not None]
    return LinhaMensal(
        ano=ano,
        mes=mes,
        chuva_mm=_soma(chuvas),
        et0_mm=_soma([d.et0 for d in dias if d.et0 is not None]),
        tmed_c=_media([d.tmed for d in dias if d.tmed is not None]),
        tmax_media_c=_media(tmaxs),
        tmin_media_c=_media(tmins),
        tmax_absoluta_c=max(tmaxs) if tmaxs else None,
        tmin_absoluta_c=min(tmins) if tmins else None,
        dias_geada=sum(t < TMIN_GEADA_C for t in tmins) if tmins else None,
        dias_calor=sum(t > tmax_calor for t in tmaxs) if tmaxs else None,
        dias_chuva_forte=sum(c > limite_forte for c in chuvas) if chuvas and limite_forte is not None else None,
        maior_seq_seca_dias=_maior_sequencia_seca(dias),
        # Dias com chuva, Tmax e Tmin presentes (os que sustentam as contagens).
        dias_validos=sum(d.chuva is not None and d.tmax is not None and d.tmin is not None for d in dias),
        gd_por_tb=gd_mensal_por_tb((tmed_do_dia(d.tmax, d.tmin) for d in dias), ano, mes),
    )


def agregar_por_mes(
    dias: list[DiaClima], limite_forte: float | None, tmax_calor: float = TMAX_CALOR_C
) -> list[LinhaMensal]:
    """Uma linha por (ano, mês) presente na série, em ordem cronológica."""
    por_mes: dict[tuple[int, int], list[DiaClima]] = {}
    for d in dias:
        por_mes.setdefault((d.data.year, d.data.month), []).append(d)
    return [_linha_do_mes(a, m, ds, limite_forte, tmax_calor) for (a, m), ds in sorted(por_mes.items())]
