"""Filtro de viabilidade: excluída, equipamento, graus-dia, geada e arroz irrigado eliminam; a água só avisa. Cada um com o motivo."""
from collections.abc import Iterable
from dataclasses import dataclass, field

from app.services import catalogo as base
from app.services.clima.graus_dia import gd_para_tb
from app.services.motor.calendario import meses_do_terco_medio
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.entradas import ClimaDoLocal, EntradasMotor
from app.services.motor.formatos import MESES, num, pct
from app.services.motor.hidrico import chuva_do_periodo, etc_mensal
from app.services.motor.modelo import Alerta, ItemRotacao
from app.services.motor.parametros import (
    AGUA_ALERTA_ABAIXO,
    AGUA_MUITO_ABAIXO,
    GD_ALERTA_ABAIXO,
    GD_ELIMINA_ABAIXO,
    GEADA_FASE_SENSIVEL,
    GEADA_MAX_FRACAO_DE_ANOS,
    GEADA_MIN_DIAS_NO_ANO,
)

ARROZ_IRRIGADO = "arroz_irrigado"


@dataclass(frozen=True)
class Achado:
    codigo: str
    texto: str
    grave: bool  # grave elimina a candidata; na rotação atual vira alerta


@dataclass
class ResultadoFiltro:
    motivos: list[str] = field(default_factory=list)  # por que foi eliminada (vazio = passou)
    alertas: list[Alerta] = field(default_factory=list)
    lacunas: list[str] = field(default_factory=list)

    @property
    def eliminada(self) -> bool:
        return bool(self.motivos)


def _gd_do_periodo(meses: list[int], tb: float, clima: ClimaDoLocal) -> float | None:
    parciais = [gd_para_tb(clima.gd_por_tb_medio.get(m), tb) for m in meses]
    return None if not parciais or any(p is None for p in parciais) else sum(parciais)


def fracao_de_anos_com_geada(meses: list[int], clima: ClimaDoLocal) -> float | None:
    """Parcela dos anos (com dado em todos os meses do período) em que algum mês teve dias de geada."""
    anos = [a for a, por_mes in clima.geada_por_ano.items() if all(por_mes.get(m) is not None for m in meses)]
    if not anos or not meses:
        return None
    com_geada = sum(any(clima.geada_por_ano[a][m] >= GEADA_MIN_DIAS_NO_ANO for m in meses) for a in anos)
    return com_geada / len(anos)


def _equipamento(c: CulturaMotor, e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    if e.equipamentos is None:
        return  # o produtor não respondeu: não filtra
    por_etapa = e.equipamentos_cultura.get(c.id)
    if por_etapa is None:
        lac.append(f"Sem lista de máquinas para {c.nome}: não checamos seus equipamentos.")
        return
    for etapa in ("plantio", "colheita"):
        servem = por_etapa.get(etapa)
        if not servem:
            lac.append(f"Sem lista de máquinas de {etapa} para {c.nome}: não checamos seus equipamentos.")
        elif not servem & e.equipamentos:
            nomes = [base.equipamentos().get(i, {}).get("nome", i) for i in sorted(servem)]
            achados.append(Achado("equipamento", f"{c.nome}: falta máquina para o {etapa}; serve {' ou '.join(nomes)}.", True))


def _graus_dia(c: CulturaMotor, meses: list[int], e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    minimo, tb = c.graus_dia_ciclo_min, c.temp_base_c
    if minimo is None or tb is None:
        if not (c.perene and minimo is None):  # pastagem: graus-dia não se aplica
            lac.append(f"{c.nome}: sem exigência de graus-dia na base, não checamos o calor do ciclo.")
        return
    gd = _gd_do_periodo(meses, tb, e.clima)
    if gd is None:
        lac.append(f"{c.nome}: sem graus-dia do clima do local para o período, não checamos o calor do ciclo.")
        return
    razao = gd / minimo  # só o mínimo conta (regra 9: a mandioca nunca é cortada pelo máximo)
    if razao < GD_ELIMINA_ABAIXO:
        achados.append(Achado("graus_dia", f"{c.nome}: o calor do período dá {num(gd, 0)} graus-dia e ela precisa de pelo menos {num(minimo, 0)}; não fecha o ciclo.", True))
    elif razao < GD_ALERTA_ABAIXO:
        achados.append(Achado("limite_termico", f"{c.nome}: no limite térmico ({num(gd, 0)} de {num(minimo, 0)} graus-dia), validar localmente.", False))


def _agua(c: CulturaMotor, item: ItemRotacao, meses: list[int], e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    if c.id == ARROZ_IRRIGADO or e.irrigacao == "sim":
        return  # arroz irrigado não passa pelo filtro de chuva (regra 8); com irrigação a falta de chuva é coberta
    chuva = chuva_do_periodo(meses, e.clima)
    if chuva is None:
        lac.append(f"{c.nome}: sem chuva do clima do local para o período, não checamos a água.")
        return
    etc_m = etc_mensal(item, c, e.clima)
    if etc_m is not None:  # Kc x ET0 do local
        etc = sum(etc_m.values())
        if etc <= 0:
            return
        razao = chuva / etc
        muito_abaixo, limite = razao < AGUA_MUITO_ABAIXO, razao < AGUA_ALERTA_ABAIXO
        falta = etc - chuva
        resumo = f"a chuva do período ({num(chuva, 0)} mm) cobre {pct(razao)} do que ela usa ({num(etc, 0)} mm)"
    elif c.agua_ciclo_mm_min is not None:  # reserva: faixa de água da base
        muito_abaixo = chuva < c.agua_ciclo_mm_min
        falta = c.agua_ciclo_mm_min - chuva
        limite = muito_abaixo or (c.agua_ciclo_mm_max is not None and chuva < c.agua_ciclo_mm_max)
        resumo = f"a chuva do período ({num(chuva, 0)} mm) fica abaixo do que ela precisa ({num(c.agua_ciclo_mm_min, 0)} a {num(c.agua_ciclo_mm_max or c.agua_ciclo_mm_min, 0)} mm)"
    else:
        lac.append(f"{c.nome}: sem Kc nem faixa de água na base, não checamos a água.")
        return
    if not limite:
        return
    # a água nunca elimina (regra 1): a chuva da estação fica abaixo da demanda onde o sequeiro é típico
    deficit = f"; faltam cerca de {num(falta, 0)} mm" if falta > 0 else ""
    complemento = "; só fecha na parte irrigada" if e.irrigacao == "parte" and muito_abaixo else ""
    achados.append(Achado("agua_no_limite", f"{c.nome}: água no limite, {resumo}{deficit}{complemento}.", False))


def _geada(c: CulturaMotor, item: ItemRotacao, meses: list[int], e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    if not c.sensivel_geada:
        return
    # fase sensível = floração: o terço do meio do ciclo (perene: o ano todo)
    fase = meses_do_terco_medio(meses) if GEADA_FASE_SENSIVEL == "terco_medio" and not item.perene else meses
    fracao = fracao_de_anos_com_geada(fase, e.clima)
    if fracao is None:
        lac.append(f"{c.nome}: sem dados de geada do local para a floração, não checamos o risco de geada.")
    elif fracao > GEADA_MAX_FRACAO_DE_ANOS:
        onde = "/".join(MESES[m - 1] for m in fase)
        achados.append(Achado("geada", f"{c.nome}: em {pct(fracao)} dos anos houve geada na fase de floração ({onde}) e ela é sensível.", True))


def achados_do_item(item: ItemRotacao, c: CulturaMotor, e: EntradasMotor, da_atual: bool) -> tuple[list[Achado], list[str]]:
    achados: list[Achado] = []
    lac: list[str] = []
    if not da_atual and c.id in e.excluidas:  # a atual é escolha do produtor; só as candidatas respeitam a exclusão
        achados.append(Achado("excluida", f"Você disse que não planta {c.nome}.", True))
    _equipamento(c, e, achados, lac)
    if c.id == ARROZ_IRRIGADO and e.irrigacao != "sim":
        achados.append(Achado("arroz_sem_irrigacao", f"{c.nome} só entra com irrigação ou várzea e você não marcou irrigação.", True))
    meses = item.meses()
    if not meses:
        lac.append(f"{c.nome}: sem os meses de plantio, não checamos clima, água e geada.")
        return achados, lac
    _graus_dia(c, meses, e, achados, lac)
    _agua(c, item, meses, e, achados, lac)
    _geada(c, item, meses, e, achados, lac)
    return achados, lac


def avaliar(itens: Iterable[ItemRotacao], e: EntradasMotor, eliminar: bool) -> ResultadoFiltro:
    """Avalia os `itens` (as culturas novas da candidata; todas, na atual). Com `eliminar`=False os graves viram alertas."""
    r = ResultadoFiltro()
    for item in itens:
        c = e.catalogo.get(item.cultura_id or "")
        if c is None:
            continue  # fora do catálogo: a lacuna "sem dados suficientes" sai nas notas
        achados, lac = achados_do_item(item, c, e, da_atual=not eliminar)
        for a in achados:
            if a.grave and eliminar:
                r.motivos.append(a.texto)
            elif a.texto not in [x.texto for x in r.alertas]:
                r.alertas.append(Alerta(a.codigo, a.texto))
        r.lacunas += [l for l in lac if l not in r.lacunas]
    return r
