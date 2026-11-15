"""Fases do ciclo em dias (regra 17): datas da fase em cada ano de plantio e anos com dias seguidos além do limiar."""
from collections.abc import Callable
from datetime import date, timedelta

from app.services.clima.agregacao import SerieDoAno
from app.services.clima.limiares import BASE_FIM, BASE_INICIO
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.formatos import MESES
from app.services.motor.modelo import ItemRotacao
from app.services.motor.parametros import DIA_DA_SEMEADURA, DIAS_POR_MES


def ciclo_em_dias(c: CulturaMotor, item: ItemRotacao) -> float | None:
    """Média de ciclo_dias_min e ciclo_dias_max (já com o arranjo regional); sem eles, o tamanho do período do item."""
    valores = [v for v in (c.ciclo_dias_min, c.ciclo_dias_max) if v is not None]
    if valores:
        return sum(valores) / len(valores)
    meses = item.meses()
    return len(meses) * DIAS_POR_MES if meses else None


def datas_da_fase(item: ItemRotacao, c: CulturaMotor, ano: int, inicio_frac: float, fim_frac: float) -> tuple[date, date] | None:
    """Primeiro e último dia da fase para o plantio de `ano`: semeadura no dia 15 do mês de início, fase em frações do ciclo.

    Perene: de 1º de janeiro a 31 de dezembro do ano. Sem mês de início ou sem ciclo: None.
    """
    if item.perene or c.perene:
        return date(ano, 1, 1), date(ano, 12, 31)
    ciclo = ciclo_em_dias(c, item)
    if item.inicio_mes is None or ciclo is None:
        return None
    semeadura = date(ano, item.inicio_mes, DIA_DA_SEMEADURA)
    return semeadura + timedelta(days=round(inicio_frac * ciclo)), semeadura + timedelta(days=round(fim_frac * ciclo))


def meses_da_fase(item: ItemRotacao, c: CulturaMotor, inicio_frac: float, fim_frac: float) -> str:
    """'set a out' (ou 'set', se cai num mês só): os meses da fase, para o texto."""
    datas = datas_da_fase(item, c, 2001, inicio_frac, fim_frac)
    if datas is None:
        return ""
    primeiro, ultimo = MESES[datas[0].month - 1], MESES[datas[1].month - 1]
    return primeiro if primeiro == ultimo else f"{primeiro} a {ultimo}"


def anos_com_sequencia(
    item: ItemRotacao,
    c: CulturaMotor,
    serie: dict[int, SerieDoAno],
    campo: str,
    inicio_frac: float,
    fim_frac: float,
    conta: Callable[[float], bool],
    dias_seguidos: int,
) -> tuple[int, int]:
    """(anos que contam, anos com dado) de 1991 a 2020, por ano de plantio.

    O ano tem dado quando todos os dias da fase têm valor (a fase pode entrar no ano seguinte, até 2021).
    Conta quando há `dias_seguidos` dias seguidos dentro da fase em que `conta(valor)` é verdadeiro.
    """
    contam = com_dado = 0
    for ano in range(BASE_INICIO, BASE_FIM + 1):
        datas = datas_da_fase(item, c, ano, inicio_frac, fim_frac)
        if datas is None:
            return 0, 0
        seguidos = maior = 0
        completo = True
        dia = datas[0]
        while dia <= datas[1]:
            s = serie.get(dia.year)
            valores = getattr(s, campo) if s is not None else []
            i = dia.timetuple().tm_yday - 1
            v = valores[i] if i < len(valores) else None
            if v is None:
                completo = False
                break
            seguidos = seguidos + 1 if conta(v) else 0
            maior = max(maior, seguidos)
            dia += timedelta(days=1)
        if completo:
            com_dado += 1
            contam += maior >= dias_seguidos
    return contam, com_dado
