"""Fazendas e climas sintéticos para os testes do motor de rotação (sem banco e sem rede)."""
import calendar
from dataclasses import MISSING, fields
from datetime import date, timedelta

from app.services.clima.agregacao import SerieDoAno
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.entradas import ClimaDoLocal, EntradasMotor
from app.services.motor.modelo import ItemRotacao
from app.services.motor.relevo_service import Relevo
from app.services.onboarding.perfil import meses_sem_cobertura

ANOS = range(1991, 2021)
PLANO = Relevo("plano", 1.0, "SRTM (teste)")


def cultura(id: str = "c", **mudancas) -> CulturaMotor:
    """Cultura comercial anual, de dados completos e confiança alta, que dá certo no clima de `clima()`."""
    base = {
        "id": id, "pais": "BR", "nome": id.capitalize(), "nome_cientifico": None, "familia_botanica": "Poaceae",
        "tipos": ("comercial",), "perene": False, "ciclo_dias_min": 100, "ciclo_dias_max": 140,
        "graus_dia_ciclo_min": 1000, "graus_dia_ciclo_max": 1500, "temp_base_c": 10, "temp_otima_min_c": None,
        "temp_otima_max_c": None, "tmax_critica_c": None, "sensivel_geada": False, "agua_ciclo_mm_min": 300,
        "agua_ciclo_mm_max": 500, "kc_inicial": 0.5, "kc_medio": 1.0, "kc_final": 0.5, "profundidade_raiz_m": 1.0,
        "fixa_nitrogenio": False, "raiz_profunda": False, "cobertura_solo": "media", "aporte_biomassa": "medio",
        "valor_forrageiro": "baixo", "confianca_parametros": "alta", "estados_validos": (),
    }  # fmt: skip
    base.update(mudancas)
    todos = {f.name for f in fields(CulturaMotor)}
    obrigatorios = {f.name for f in fields(CulturaMotor) if f.default is MISSING and f.default_factory is MISSING}
    assert obrigatorios <= set(base) <= todos  # campos com valor padrão (janela, régua, extras...) são opcionais
    return CulturaMotor(**base)


ANOS_GD = range(2001, 2022)  # 2001–2020 mais 2021, que fecha a safra de 2020 que atravessa o ano


def serie_diaria(tmin=15.0, tmax=25.0, anos=range(1991, 2022), dias: dict | None = None) -> dict[int, SerieDoAno]:
    """Série diária sintética (índice 0 = 1º de janeiro): Tmin e Tmax constantes, com `dias` = {data: {"tmin": x, "tmax": y}} trocando valores (None = sem dado)."""
    saida = {a: SerieDoAno(a, [tmin] * (366 if calendar.isleap(a) else 365), [tmax] * (366 if calendar.isleap(a) else 365)) for a in anos}
    for d, v in (dias or {}).items():
        if d.year in saida:
            i = d.timetuple().tm_yday - 1
            if "tmin" in v:
                saida[d.year].tmin_c[i] = v["tmin"]
            if "tmax" in v:
                saida[d.year].tmax_c[i] = v["tmax"]
    return saida


def episodio(anos, mes: int, dia: int, n: int, **valores) -> dict:
    """`n` dias seguidos a partir de mes/dia em cada um dos `anos`, com os `valores` (tmin=..., tmax=...) para `serie_diaria`."""
    return {date(a, mes, dia) + timedelta(days=k): valores for a in anos for k in range(n)}


def clima(chuva=100.0, et0=100.0, tmed=25.0, forte=1.0, geada: dict[int, int] | None = None, tmed_por_ano: dict | None = None, serie: dict | None = None) -> ClimaDoLocal:
    """Cada argumento aceita um número (todos os meses) ou uma lista de 12.

    `geada` = {mês: nº de anos (dos 30) com dia de geada nesse mês}. GD do mês = (tmed - Tb) x 30, sem teto.
    `serie` = série diária por ano (ver `serie_diaria`); sem ela, Tmin 15 °C e Tmax 25 °C em todos os dias de 1991 a 2021 ({} = sem série).
    `tmed_por_ano` = {ano: tmed (número ou lista de 12)} troca a temperatura desse ano; None no lugar do ano tira o ano do GD.
    """

    def doze(v):
        return list(v) if isinstance(v, (list, tuple)) else [v] * 12

    ch, e0, tm, fo = doze(chuva), doze(et0), doze(tmed), doze(forte)
    geada = geada or {}
    por_ano = tmed_por_ano or {}

    def gd_do_ano(ano):
        t = doze(por_ano[ano]) if ano in por_ano else tm
        return {m: {str(tb): max(0.0, t[m - 1] - tb) * 30 for tb in range(0, 21)} for m in range(1, 13)}

    return ClimaDoLocal(
        fonte="NASA POWER (teste)",
        periodo="1991–2020",
        chuva_mm={m: ch[m - 1] for m in range(1, 13)},
        et0_mm={m: e0[m - 1] for m in range(1, 13)},
        dias_chuva_forte={m: fo[m - 1] for m in range(1, 13)},
        geada_por_ano={a: {m: int(i < geada.get(m, 0)) for m in range(1, 13)} for i, a in enumerate(ANOS)},
        serie_diaria=serie if serie is not None else serie_diaria(),
        gd_por_tb_ano={a: gd_do_ano(a) for a in ANOS_GD if por_ano.get(a, 0) is not None},
    )


def item(cultura_id: str | None, inicio: int | None, fim: int | None, perene: bool = False, texto: str | None = None) -> ItemRotacao:
    return ItemRotacao(cultura_id, inicio, fim, perene, texto or f"{cultura_id} ({inicio}-{fim})")


def entradas(atual: list[ItemRotacao], culturas: list[CulturaMotor], **mudancas) -> EntradasMotor:
    """Entradas do motor com clima de `clima()`, sem relevo e sem restrições (muda com os argumentos)."""
    dados = {
        "pais": "BR", "catalogo": {c.id: c for c in culturas}, "atual": tuple(atual),
        "meses_vazios": meses_sem_cobertura(atual), "clima": clima(), "relevo": None, "irrigacao": "nao",
    }  # fmt: skip
    dados.update(mudancas)
    return EntradasMotor(**dados)
