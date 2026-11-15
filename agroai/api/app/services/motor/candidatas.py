"""Candidatas: a rotação atual mais três regras (janela vazia, troca por tolerante à seca, leguminosa); coberturas seguem a janela (regra 12)."""
from dataclasses import dataclass

from app.services.motor.calendario import maior_janela_vazia, meses_do_periodo, meses_necessarios, meses_para_dias
from app.services.motor.catalogo import CulturaMotor, janela_de_semeadura
from app.services.motor.formatos import periodo_texto
from app.services.motor.modelo import Alerta, Estrategia, ItemRotacao
from app.services.motor.parametros import CEREAIS_INVERNO

A_LANCO = "a_lanco_lavoura_em_pe"  # só informação (regra 12): nunca vira sugestão


@dataclass(frozen=True)
class Colocacao:
    """Os itens da rotação com a cultura nova no lugar e os avisos da montagem."""

    itens: tuple[ItemRotacao, ...]
    alertas: tuple[Alerta, ...] = ()


def chave(e: Estrategia) -> frozenset[tuple]:
    """Identidade da estratégia: os mesmos itens (cultura, meses), em qualquer ordem."""
    return frozenset((i.cultura_id, i.inicio_mes, i.fim_mes, i.perene) for i in e.itens)


def _item_na_janela(c: CulturaMotor, inicio: int, n_janela: int) -> ItemRotacao | None:
    """Cultura plantada no início da janela, pelo menos o ciclo mínimo (meses inteiros). None se não couber."""
    if c.perene or c.ciclo_dias_min is None or c.ciclo_dias_min > meses_para_dias(n_janela):
        return None
    n = min(meses_necessarios(c.ciclo_dias_min), n_janela)
    fim = (inicio - 1 + n - 1) % 12 + 1
    return ItemRotacao(c.id, inicio, fim, False, f"{c.nome} ({periodo_texto(inicio, fim, False)})")


def _nome_do_item(i: ItemRotacao, catalogo: dict[str, CulturaMotor]) -> str:
    return catalogo[i.cultura_id].nome if i.cultura_id in catalogo else i.texto


def _serve_depois_de(condicao: str, x: CulturaMotor) -> bool:
    if condicao == "apos_colheita_graos":
        return x.tem_tipo("comercial") and not x.perene
    if condicao == "apos_cereal_inverno":
        return x.id in CEREAIS_INVERNO
    return False  # apos_silagem: o calendário não diz se foi silagem; a_lanco: só informação


def _anterior(itens: tuple[ItemRotacao, ...], inicio: int, ignorar: ItemRotacao | None) -> ItemRotacao | None:
    """X: o item que termina no mês imediatamente antes do início do lugar."""
    antes = (inicio - 2) % 12 + 1
    return next((i for i in itens if i is not ignorar and not i.perene and i.fim_mes == antes), None)


def _mes_de_plantio_da_cobertura(
    c: CulturaMotor,
    lugar: list[int],
    itens: tuple[ItemRotacao, ...],
    catalogo: dict[str, CulturaMotor],
    estado: str | None,
    ignorar: ItemRotacao | None = None,
) -> tuple[int, tuple[Alerta, ...]] | None:
    """Regra 12: mês em que a cobertura é semeada no `lugar` (meses em ordem) e os avisos; None = não cabe ali."""
    j = janela_de_semeadura(c, estado)
    if j is None:
        return lugar[0], (Alerta("janela_nao_confirmada", f"{c.nome}: a época de semeadura ainda não foi confirmada para a sua região."),)
    semeadura = set(meses_do_periodo(j.inicio[0], j.fim[0], False))  # meses inteiros; dá a volta no ano
    inicio = lugar[0]
    colheita_de_x = (inicio - 2) % 12 + 1
    p = inicio if colheita_de_x in semeadura or inicio in semeadura else next((m for m in lugar if m in semeadura), None)
    if p is None:
        return None
    if c.ciclo_dias_min is not None and c.ciclo_dias_min > meses_para_dias(len(lugar) - lugar.index(p)):
        return None  # o ciclo mínimo não cabe de p até o fim do lugar
    alertas: tuple[Alerta, ...] = ()
    if j.condicao_semeadura:
        validas = [k for k in j.condicao_semeadura if k != A_LANCO]
        if not validas:
            return None
        x = _anterior(itens, inicio, ignorar)
        if x is not None:
            cx = catalogo.get(x.cultura_id or "")
            if cx is None:
                alertas = (Alerta("janela_nao_confirmada", f"{c.nome}: confira se dá para semear depois de {_nome_do_item(x, catalogo)}."),)
            elif not any(_serve_depois_de(k, cx) for k in validas):
                return None
    return p, alertas


def _na_janela_vazia(c: CulturaMotor, janela: tuple[int, int], atual: Estrategia, catalogo: dict[str, CulturaMotor], estado: str | None) -> Colocacao | None:
    inicio, n = janela
    if not c.e_cobertura:
        item = _item_na_janela(c, inicio, n)
        return None if item is None else Colocacao(atual.itens + (item,))
    lugar = [(inicio - 1 + i) % 12 + 1 for i in range(n)]
    achado = _mes_de_plantio_da_cobertura(c, lugar, atual.itens, catalogo, estado)
    if achado is None:
        return None
    p, alertas = achado
    item = _item_na_janela(c, p, n - lugar.index(p))
    return None if item is None else Colocacao(atual.itens + (item,), alertas)


def _trocar(atual: Estrategia, pos: int, nova: CulturaMotor) -> tuple[ItemRotacao, ...]:
    velho = atual.itens[pos]
    item = ItemRotacao(nova.id, velho.inicio_mes, velho.fim_mes, False, f"{nova.nome} ({periodo_texto(velho.inicio_mes, velho.fim_mes, False)})")
    return atual.itens[:pos] + (item,) + atual.itens[pos + 1 :]


def _trocar_por(atual: Estrategia, pos: int, nova: CulturaMotor, catalogo: dict[str, CulturaMotor], estado: str | None) -> Colocacao | None:
    velho = atual.itens[pos]
    lugar = velho.meses()
    if not nova.e_cobertura or not lugar:
        return Colocacao(_trocar(atual, pos, nova))
    achado = _mes_de_plantio_da_cobertura(nova, lugar, atual.itens, catalogo, estado, ignorar=velho)
    if achado is None:
        return None
    p, alertas = achado
    if p == lugar[0]:
        return Colocacao(_trocar(atual, pos, nova), alertas)
    item = ItemRotacao(nova.id, p, velho.fim_mes, False, f"{nova.nome} ({periodo_texto(p, velho.fim_mes, False)})")  # empurrada para o início da janela
    return Colocacao(atual.itens[:pos] + (item,) + atual.itens[pos + 1 :], alertas)


def _principal(atual: tuple[ItemRotacao, ...], catalogo: dict[str, CulturaMotor]) -> int | None:
    """Posição da cultura principal: a comercial de ciclo mais longo (ciclo máximo) entre as da rotação atual."""
    achados = [
        (catalogo[i.cultura_id].ciclo_dias_max, -pos)
        for pos, i in enumerate(atual)
        if i.cultura_id in catalogo and catalogo[i.cultura_id].tem_tipo("comercial") and catalogo[i.cultura_id].ciclo_dias_max
    ]
    return None if not achados else -max(achados)[1]


def gerar_candidatas(atual: Estrategia, catalogo: dict[str, CulturaMotor], meses_vazios: list[int], estado: str | None = None) -> list[Estrategia]:
    """Candidatas sem repetir itens e sem a atual, todas (sem corte; ordem: janela, tolerante à seca, leguminosa).

    Só entram culturas válidas no `estado` da fazenda (regra 13); as da atual continuam no catálogo para as contas.
    Coberturas só entram onde a janela de semeadura e a cultura anterior permitem (regra 12).
    """
    novas = [c for c in catalogo.values() if c.vale_em(estado)]
    vistos = {chave(atual)}
    saida: list[Estrategia] = []

    def adicionar(id_: str, nome: str, origem: str, col: Colocacao) -> None:
        e = Estrategia(id_, nome, origem, col.itens, col.alertas)  # type: ignore[arg-type]
        if chave(e) not in vistos:
            vistos.add(chave(e))
            saida.append(e)

    ja_na_atual = {i.cultura_id for i in atual.itens}
    janela = maior_janela_vazia(meses_vazios)

    def na_janela(c: CulturaMotor) -> Colocacao | None:
        return None if janela is None else _na_janela_vazia(c, janela, atual, catalogo, estado)

    def periodo_do_novo(col: Colocacao) -> str:
        novo = col.itens[-1]
        return periodo_texto(novo.inicio_mes, novo.fim_mes, False)

    # 1. Janela vazia: cada cultura cujo ciclo mínimo cabe na maior janela contínua
    for c in novas:
        if (col := na_janela(c)) is not None:
            adicionar(f"janela:{c.id}", f"Plantar {c.nome} no período vazio ({periodo_do_novo(col)})", "janela", col)

    # 2. A principal trocada por cada cultura tolerante à seca, no mesmo período
    pos = _principal(atual.itens, catalogo)
    if pos is not None and not atual.itens[pos].perene:
        velha = catalogo[atual.itens[pos].cultura_id]
        for c in novas:
            if c.tem_tipo("tolerante_seca") and not c.perene and c.id not in ja_na_atual:
                if (col := _trocar_por(atual, pos, c, catalogo, estado)) is not None:
                    adicionar(f"tolerante_seca:{velha.id}->{c.id}", f"Trocar {velha.nome} por {c.nome}", "tolerante_seca", col)

    # 3. Uma leguminosa (fixadora de N): na janela vazia ou no lugar de uma cultura que não é a principal
    for c in novas:
        if not c.tem_tipo("fixadora_n") or c.perene:
            continue
        if (col := na_janela(c)) is not None:
            adicionar(f"leguminosa:janela:{c.id}", f"Plantar {c.nome} no período vazio ({periodo_do_novo(col)})", "leguminosa", col)
        if c.id in ja_na_atual:
            continue
        for p, velho in enumerate(atual.itens):
            ja_fixa = velho.cultura_id in catalogo and catalogo[velho.cultura_id].fixa_nitrogenio  # trocar leguminosa por leguminosa não inclui nada
            if p != pos and not velho.perene and velho.cultura_id != c.id and velho.inicio_mes is not None and not ja_fixa:
                if (col := _trocar_por(atual, p, c, catalogo, estado)) is not None:
                    adicionar(f"leguminosa:{velho.cultura_id or p}->{c.id}", f"Trocar {_nome_do_item(velho, catalogo)} por {c.nome}", "leguminosa", col)

    return saida
