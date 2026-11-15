"""Água da cultura: ETc = Kc x ET0 por mês (Kc inicial, médio e final nos terços do ciclo) e chuva do período."""
from app.services.motor.calendario import partes_por_terco
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.entradas import ClimaDoLocal
from app.services.motor.modelo import ItemRotacao


def chuva_do_periodo(meses: list[int], clima: ClimaDoLocal) -> float | None:
    """Chuva média (1991–2020) somada nos meses; None se faltar algum mês."""
    valores = [clima.chuva_mm.get(m) for m in meses]
    return None if not valores or any(v is None for v in valores) else sum(valores)


def etc_mensal(item: ItemRotacao, cultura: CulturaMotor, clima: ClimaDoLocal) -> dict[int, float] | None:
    """ETc (mm) de cada mês do item. Perene: Kc médio o ano todo. None se faltar Kc, ET0 ou os meses."""
    meses = item.meses()
    kcs = (cultura.kc_inicial, cultura.kc_medio, cultura.kc_final)
    if not meses or any(k is None for k in kcs) or any(clima.et0_mm.get(m) is None for m in meses):
        return None
    if item.perene:
        return {m: cultura.kc_medio * clima.et0_mm[m] for m in meses}
    partes = partes_por_terco(len(meses))
    return {m: sum(kcs[t] * clima.et0_mm[m] * f for t, f in partes[i]) for i, m in enumerate(meses)}
