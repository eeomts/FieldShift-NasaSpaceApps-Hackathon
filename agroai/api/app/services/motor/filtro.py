"""Filtro de viabilidade: excluída, equipamento, graus-dia (só culturas de venda), geada/frio e arroz irrigado eliminam; a água só avisa. Cada um com o motivo."""
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, timedelta

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
    FASE_FRIO_PADRAO,
    FASE_FRIO_PERENE,
    FASES_FRIO_TEXTO,
    FRIO_MIN_ANOS_COM_DADO,
    GD_ALERTA_ABAIXO,
    GD_ELIMINA_ABAIXO,
    GEADA_FASE_SENSIVEL,
    GEADA_MAX_FRACAO_DE_ANOS,
    GEADA_MIN_DIAS_NO_ANO,
    SEMEADURA_DIA_DO_MES,
    TMIN_ANO_FIM,
    TMIN_ANO_INICIO,
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


def janela_do_frio(c: CulturaMotor, item: ItemRotacao, ano: int) -> tuple[date, date] | None:
    """Dias (início, fim, inclusive) da fase sensível ao frio no ano de semeadura `ano` (regra 17).

    Perene: o ano todo. Senão: semeadura no dia SEMEADURA_DIA_DO_MES de `inicio_mes` + fração × ciclo médio da base;
    fração vazia = o ciclo inteiro. Sem ciclo na base: None.
    """
    if item.perene:
        return date(ano, 1, 1), date(ano, 12, 31)
    ciclos = [v for v in (c.ciclo_dias_min, c.ciclo_dias_max) if v is not None]
    if not ciclos or item.inicio_mes is None:
        return None
    ciclo = sum(ciclos) / len(ciclos)
    semeadura = date(ano, item.inicio_mes, SEMEADURA_DIA_DO_MES)
    ini = 0.0 if c.fase_frio_inicio_frac is None else c.fase_frio_inicio_frac
    fim = 1.0 if c.fase_frio_fim_frac is None else c.fase_frio_fim_frac
    return semeadura + timedelta(days=round(ini * ciclo)), semeadura + timedelta(days=round(fim * ciclo))


def _ano_com_frio(janela: tuple[date, date], limiar: float, seguidos: int, clima: ClimaDoLocal) -> bool | None:
    """O ano teve `seguidos` dias seguidos com Tmin < limiar na janela? None se algum dia da janela não tem dado."""
    ini, fim = janela
    temps = [clima.tmin_por_dia.get(ini + timedelta(days=i)) for i in range((fim - ini).days + 1)]
    if any(t is None for t in temps):
        return None
    corrida = 0
    for t in temps:
        corrida = corrida + 1 if t < limiar else 0
        if corrida >= seguidos:
            return True
    return False


def anos_com_frio(c: CulturaMotor, item: ItemRotacao, clima: ClimaDoLocal) -> list[bool] | None:
    """Para cada ano de semeadura 1991-2020 com todos os dias da fase presentes: o frio da regra 17 ocorreu?

    Ano com algum dia sem dado fica de fora (a lista pode ter menos de 30). None: sem limiar na base ou sem ciclo para
    montar a janela da fase.
    """
    if c.tmin_critica_c is None:
        return None
    resultados = []
    for ano in range(TMIN_ANO_INICIO, TMIN_ANO_FIM + 1):
        janela = janela_do_frio(c, item, ano)
        if janela is None:
            return None
        r = _ano_com_frio(janela, c.tmin_critica_c, c.dias_seguidos_de_frio, clima)
        if r is not None:
            resultados.append(r)
    return resultados


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
        calor = f"{c.nome}: o calor do período dá {num(gd, 0)} graus-dia e ela precisa de pelo menos {num(minimo, 0)}"
        if c.tem_tipo("comercial"):
            achados.append(Achado("graus_dia", f"{calor}; não fecha o ciclo.", True))
        else:  # cobertura: o produtor corta antes do fim do ciclo, então só avisa
            achados.append(Achado("graus_dia", f"{calor}; pode não completar o ciclo antes do manejo.", False))
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


def _frio(c: CulturaMotor, item: ItemRotacao, e: EntradasMotor, achados: list[Achado], lac: list[str]) -> None:
    """Regra 17: limiar de Tmin da cultura, só nos dias da fase sensível. Sem dado diário: lacuna, nunca o limiar de 2 °C."""
    limiar = c.tmin_critica_c
    onde = FASE_FRIO_PERENE if item.perene else FASES_FRIO_TEXTO.get(c.fase_sensivel_frio or "", FASE_FRIO_PADRAO)
    anos = anos_com_frio(c, item, e.clima)
    if anos is None:  # sem ciclo na base: não dá para montar a janela da fase
        lac.append(f"{c.nome}: sem o ciclo na base, não checamos o frio.")
        return
    if not anos:
        lac.append(f"{c.nome}: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio {onde}.")
        return
    total = TMIN_ANO_FIM - TMIN_ANO_INICIO + 1
    if len(anos) < FRIO_MIN_ANOS_COM_DADO:
        lac.append(f"{c.nome}: o frio {onde} foi checado em só {len(anos)} dos {total} anos, por falta de temperatura mínima do local; poucos para decidir.")
        return
    fracao = sum(anos) / len(anos)
    if fracao <= GEADA_MAX_FRACAO_DE_ANOS:
        return
    termo = "geada" if limiar <= 0 else "frio"
    graus = num(limiar, 1).removesuffix(",0")
    seguidos = c.dias_seguidos_de_frio
    quanto = f"mínima abaixo de {graus} °C" + (f" por {seguidos} dias seguidos" if seguidos > 1 else "")
    if c.tmin_efeito == "aviso":  # dano parcial (ex.: esterilidade do arroz): fica, com o aviso
        achados.append(Achado(termo, f"{c.nome}: {termo} {onde} em {pct(fracao)} dos anos ({quanto}); o dano é parcial, validar localmente.", False))
    else:
        achados.append(Achado(termo, f"{c.nome}: em {pct(fracao)} dos anos houve {termo} {onde} ({quanto}) e ela é sensível.", True))


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
    if c.tmin_critica_c is not None:
        _frio(c, item, e, achados, lac)
    else:
        _geada(c, item, meses, e, achados, lac)  # reserva: 2 °C no terço do meio, para cultura sem limiar na base
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
