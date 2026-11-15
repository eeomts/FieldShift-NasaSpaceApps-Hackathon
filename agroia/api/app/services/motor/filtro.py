"""Filtro de viabilidade: excluída, equipamento, graus-dia, geada, arroz irrigado e chuva muito curta (só sugestões) eliminam; calor e água no limite avisam."""
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from app.services import catalogo as base
from app.services.clima.agregacao import percentil
from app.services.clima.graus_dia import gd_para_tb
from app.services.clima.limiares import BASE_FIM, BASE_INICIO
from app.services.motor.calendario import meses_do_terco_medio
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.entradas import ClimaDoLocal, EntradasMotor
from app.services.motor.formatos import MESES, inteiro, num, pct
from app.services.motor.hidrico import chuva_do_periodo, etc_mensal
from app.services.motor.modelo import Alerta, ItemRotacao
from app.services.motor.parametros import (
    AGUA_ALERTA_ABAIXO,
    AGUA_ELIMINA_SUGESTAO_ABAIXO,
    AGUA_MUITO_ABAIXO,
    CALOR_FASE_SENSIVEL,
    CALOR_MAX_FRACAO_DE_ANOS,
    GD_ALERTA_ABAIXO,
    GD_ANO_FIM,
    GD_ANO_INICIO,
    GD_ELIMINA_ABAIXO,
    GD_MIN_SAFRAS,
    GD_PERCENTIL_ANO_FRIO,
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
    texto_alerta: str | None = None  # texto do alerta na rotação atual, quando difere do motivo de eliminação


@dataclass
class ResultadoFiltro:
    motivos: list[str] = field(default_factory=list)  # por que foi eliminada (vazio = passou)
    alertas: list[Alerta] = field(default_factory=list)
    lacunas: list[str] = field(default_factory=list)

    @property
    def eliminada(self) -> bool:
        return bool(self.motivos)


def gd_das_safras(meses: list[int], tb: float, clima: ClimaDoLocal) -> list[float]:
    """Graus-dia de cada safra com ano de plantio em 2001–2020. Os meses do período vêm em ordem: quando o mês
    volta (dez -> jan) o ciclo entrou no ano seguinte. Safra com algum mês sem GD completo fica de fora."""
    safras = []
    for plantio in range(GD_ANO_INICIO, GD_ANO_FIM + 1):
        ano, anterior, total = plantio, 0, 0.0
        for m in meses:
            ano += m < anterior
            anterior = m
            parcial = gd_para_tb(clima.gd_por_tb_ano.get(ano, {}).get(m), tb)
            if parcial is None:
                break
            total += parcial
        else:
            safras.append(total)
    return safras


def _fracao_de_anos(meses: list[int], por_ano: dict[int, dict[int, Any]], conta: Callable[[Any], bool]) -> float | None:
    """Parcela dos anos (com dado em todos os meses do período) em que algum mês satisfaz `conta`."""
    anos = [a for a, por_mes in por_ano.items() if all(por_mes.get(m) is not None for m in meses)]
    if not anos or not meses:
        return None
    return sum(any(conta(por_ano[a][m]) for m in meses) for a in anos) / len(anos)


def fracao_de_anos_com_geada(meses: list[int], clima: ClimaDoLocal) -> float | None:
    """Parcela dos anos (com dado em todos os meses do período) em que algum mês teve dias de geada."""
    return _fracao_de_anos(meses, clima.geada_por_ano, lambda dias: dias >= GEADA_MIN_DIAS_NO_ANO)


def fracao_de_anos_com_calor(meses: list[int], limite_c: float, clima: ClimaDoLocal) -> float | None:
    """Parcela dos anos (com dado em todos os meses do período) em que a máxima de algum mês passou de `limite_c`."""
    return _fracao_de_anos(meses, clima.tmax_absoluta_por_ano, lambda tmax: tmax > limite_c)


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


def _regiao(c: CulturaMotor, e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    """Regra 13: base da cultura válida só em certos estados. Fora da lista, só avisa (a candidata nem é gerada)."""
    if not c.estados_validos:
        return  # vazio = sem restrição
    if e.estado is None:
        lac.append(f"{c.nome}: não sabemos o estado da fazenda, então não checamos se a base dela vale para sua região.")
    elif not c.vale_em(e.estado):
        achados.append(Achado("sem_dado_regiao", f"{c.nome}: sem dado para sua região ({e.estado}); a base dela vale para {', '.join(c.estados_validos)}.", False))


def _graus_dia(c: CulturaMotor, meses: list[int], e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    minimo, tb = c.graus_dia_ciclo_min, c.temp_base_c
    if c.perene and (minimo is None or c.tem_tipo("forrageira")):
        return  # regra 14: perene forrageira (pastagem, alfafa) não tem filtro de ciclo nem de graus-dia; vazio = não se aplica
    if minimo is None or tb is None:
        lac.append(f"{c.nome}: sem exigência de graus-dia na base, não checamos o calor do ciclo.")
        return
    safras = gd_das_safras(meses, tb, e.clima)
    if not safras:
        lac.append(f"{c.nome}: sem graus-dia do clima do local para o período, não checamos o calor do ciclo.")
        return
    if len(safras) < GD_MIN_SAFRAS:
        lac.append(f"{c.nome}: sem anos suficientes de clima para checar o calor do ciclo.")
        return
    mediana = percentil(safras, 50)  # regra 2: a mediana dos anos, não o ano a ano
    razao = mediana / minimo  # só o mínimo conta (regra 9: a mandioca nunca é cortada pelo máximo)
    periodo = f"{GD_ANO_INICIO}–{GD_ANO_FIM}"
    calor = f"o calor do período dá {inteiro(mediana)} graus-dia na metade dos anos ({periodo}) e ela precisa de pelo menos {inteiro(minimo)}"
    if c.e_cobertura:  # coberturas: o calor nunca elimina, quem decide se cabe é a janela (regra 12)
        if razao < GD_ALERTA_ABAIXO:
            achados.append(Achado("pouco_crescimento", f"{c.nome}: pouco crescimento antes do frio ou do manejo; {calor}.", False))
        return
    if razao < GD_ELIMINA_ABAIXO:
        achados.append(Achado("graus_dia", f"{c.nome}: {calor}; não fecha o ciclo.", True))
        return
    if razao < GD_ALERTA_ABAIXO:
        achados.append(Achado("limite_termico", f"{c.nome}: no limite térmico, validar localmente; {calor}.", False))
    p10 = percentil(safras, GD_PERCENTIL_ANO_FRIO)
    if p10 < GD_ELIMINA_ABAIXO * minimo:
        achados.append(Achado("ano_frio", f"{c.nome}: em ano frio pode não completar o ciclo; em 1 a cada 10 anos ({periodo}) o calor do período fica em {inteiro(p10)} graus-dia, e ela precisa de pelo menos {inteiro(minimo)}.", False))


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
        elimina = razao < AGUA_ELIMINA_SUGESTAO_ABAIXO
        motivo = f"{c.nome}: a chuva do período ({num(chuva, 0)} mm) cobre só {pct(razao)} da água que a cultura usa ({num(etc, 0)} mm); sem irrigação não fecha."
        falta = etc - chuva
        resumo = f"a chuva do período ({num(chuva, 0)} mm) cobre {pct(razao)} do que ela usa ({num(etc, 0)} mm)"
    elif c.agua_ciclo_mm_min is not None:  # reserva: faixa de água da base
        muito_abaixo = chuva < c.agua_ciclo_mm_min
        falta = c.agua_ciclo_mm_min - chuva
        limite = muito_abaixo or (c.agua_ciclo_mm_max is not None and chuva < c.agua_ciclo_mm_max)
        elimina = chuva < AGUA_ELIMINA_SUGESTAO_ABAIXO * c.agua_ciclo_mm_min  # sem a conta local: a mesma razão contra o mínimo da base
        motivo = f"{c.nome}: a chuva do período ({num(chuva, 0)} mm) cobre só {pct(chuva / c.agua_ciclo_mm_min)} da água que a cultura precisa ({num(c.agua_ciclo_mm_min, 0)} mm); sem irrigação não fecha."
        resumo = f"a chuva do período ({num(chuva, 0)} mm) fica abaixo do que ela precisa ({num(c.agua_ciclo_mm_min, 0)} a {num(c.agua_ciclo_mm_max or c.agua_ciclo_mm_min, 0)} mm)"
    else:
        lac.append(f"{c.nome}: sem Kc nem faixa de água na base, não checamos a água.")
        return
    if not limite:
        return
    deficit = f"; faltam cerca de {num(falta, 0)} mm" if falta > 0 else ""
    complemento = "; só fecha na parte irrigada" if e.irrigacao == "parte" and muito_abaixo else ""
    aviso = f"{c.nome}: água no limite, {resumo}{deficit}{complemento}."
    # só a sugestão nova é eliminada (a rotação atual vira aviso, em `avaliar`); com irrigação em parte da área, só avisa
    if elimina and e.irrigacao != "parte":
        achados.append(Achado("agua_no_limite", motivo, True, aviso))
    else:
        achados.append(Achado("agua_no_limite", aviso, False))


def _fase_sensivel(item: ItemRotacao, meses: list[int], modo: str) -> list[int]:
    """Fase sensível = floração: o terço do meio do ciclo (perene: o ano todo)."""
    return meses_do_terco_medio(meses) if modo == "terco_medio" and not item.perene else meses


def _calor(c: CulturaMotor, item: ItemRotacao, meses: list[int], e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    """Regra 11: só avisa; tmax_critica_c vazio = sem aviso e sem lacuna."""
    limite = c.tmax_critica_c
    if limite is None:
        return
    fase = _fase_sensivel(item, meses, CALOR_FASE_SENSIVEL)
    fracao = fracao_de_anos_com_calor(fase, limite, e.clima)
    if fracao is None:
        lac.append(f"{c.nome}: sem dados de temperatura máxima do local para a floração, não checamos o risco de calor.")
    elif fracao > CALOR_MAX_FRACAO_DE_ANOS:
        graus = num(limite, 0 if limite == int(limite) else 1)
        fase_txt = "ao longo do ano" if item.perene else f"na floração ({_meses_a(fase)})"
        achados.append(Achado("calor_floracao", f"{c.nome}: em {pct(fracao)} dos anos ({BASE_INICIO}–{BASE_FIM}) a temperatura passou de {graus} °C {fase_txt}; o calor nessa fase pode reduzir a produção.", False))


def _meses_a(fase: list[int]) -> str:
    return MESES[fase[0] - 1] if len(fase) == 1 else f"{MESES[fase[0] - 1]} a {MESES[fase[-1] - 1]}"


def _geada(c: CulturaMotor, item: ItemRotacao, meses: list[int], e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    if not c.sensivel_geada:
        return
    fase = _fase_sensivel(item, meses, GEADA_FASE_SENSIVEL)
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
    _regiao(c, e, achados, lac)
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
    _calor(c, item, meses, e, achados, lac)
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
            elif (a.texto_alerta or a.texto) not in [x.texto for x in r.alertas]:
                r.alertas.append(Alerta(a.codigo, a.texto_alerta or a.texto))
        r.lacunas += [l for l in lac if l not in r.lacunas]
    return r
