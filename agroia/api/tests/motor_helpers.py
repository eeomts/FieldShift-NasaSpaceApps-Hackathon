"""Fazendas e climas sintéticos para os testes do motor de rotação (sem banco e sem rede)."""
from dataclasses import MISSING, fields

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


def clima(chuva=100.0, et0=100.0, tmed=25.0, forte=1.0, geada: dict[int, int] | None = None) -> ClimaDoLocal:
    """Cada argumento aceita um número (todos os meses) ou uma lista de 12.

    `geada` = {mês: nº de anos (dos 30) com dia de geada nesse mês}. GD do mês = (tmed - Tb) x 30, sem teto.
    """

    def doze(v):
        return list(v) if isinstance(v, (list, tuple)) else [v] * 12

    ch, e0, tm, fo = doze(chuva), doze(et0), doze(tmed), doze(forte)
    geada = geada or {}
    return ClimaDoLocal(
        fonte="NASA POWER (teste)",
        periodo="1991–2020",
        chuva_mm={m: ch[m - 1] for m in range(1, 13)},
        et0_mm={m: e0[m - 1] for m in range(1, 13)},
        dias_chuva_forte={m: fo[m - 1] for m in range(1, 13)},
        geada_por_ano={a: {m: int(i < geada.get(m, 0)) for m in range(1, 13)} for i, a in enumerate(ANOS)},
        gd_por_tb_medio={m: {str(tb): max(0.0, tm[m - 1] - tb) * 30 for tb in range(0, 21)} for m in range(1, 13)},
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
