"""Candidatas: a rotação atual mais três regras (janela vazia, troca por tolerante à seca, leguminosa)."""
from app.services.motor.calendario import maior_janela_vazia, meses_necessarios, meses_para_dias
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.formatos import periodo_texto
from app.services.motor.modelo import Estrategia, ItemRotacao
from app.services.motor.parametros import MAX_CANDIDATAS


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


def _principal(atual: tuple[ItemRotacao, ...], catalogo: dict[str, CulturaMotor]) -> int | None:
    """Posição da cultura principal: a comercial de ciclo mais longo (ciclo máximo) entre as da rotação atual."""
    achados = [
        (catalogo[i.cultura_id].ciclo_dias_max, -pos)
        for pos, i in enumerate(atual)
        if i.cultura_id in catalogo and catalogo[i.cultura_id].tem_tipo("comercial") and catalogo[i.cultura_id].ciclo_dias_max
    ]
    return None if not achados else -max(achados)[1]


def _trocar(atual: Estrategia, pos: int, nova: CulturaMotor) -> tuple[ItemRotacao, ...]:
    velho = atual.itens[pos]
    item = ItemRotacao(nova.id, velho.inicio_mes, velho.fim_mes, False, f"{nova.nome} ({periodo_texto(velho.inicio_mes, velho.fim_mes, False)})")
    return atual.itens[:pos] + (item,) + atual.itens[pos + 1 :]


def _nome_do_item(i: ItemRotacao, catalogo: dict[str, CulturaMotor]) -> str:
    return catalogo[i.cultura_id].nome if i.cultura_id in catalogo else i.texto


def gerar_candidatas(atual: Estrategia, catalogo: dict[str, CulturaMotor], meses_vazios: list[int]) -> list[Estrategia]:
    """Candidatas sem repetir itens e sem a atual, no máximo MAX_CANDIDATAS (ordem: janela, tolerante à seca, leguminosa)."""
    vistos = {chave(atual)}
    saida: list[Estrategia] = []

    def adicionar(id_: str, nome: str, origem: str, itens: tuple[ItemRotacao, ...]) -> None:
        e = Estrategia(id_, nome, origem, itens)  # type: ignore[arg-type]
        if chave(e) not in vistos:
            vistos.add(chave(e))
            saida.append(e)

    ja_na_atual = {i.cultura_id for i in atual.itens}
    janela = maior_janela_vazia(meses_vazios)

    def na_janela(c: CulturaMotor) -> ItemRotacao | None:
        return None if janela is None else _item_na_janela(c, *janela)

    # 1. Janela vazia: cada cultura cujo ciclo mínimo cabe na maior janela contínua
    for c in catalogo.values():
        if (item := na_janela(c)) is not None:
            adicionar(f"janela:{c.id}", f"Plantar {c.nome} no período vazio ({periodo_texto(item.inicio_mes, item.fim_mes, False)})", "janela", atual.itens + (item,))

    # 2. A principal trocada por cada cultura tolerante à seca, no mesmo período
    pos = _principal(atual.itens, catalogo)
    if pos is not None and not atual.itens[pos].perene:
        velha = catalogo[atual.itens[pos].cultura_id]
        for c in catalogo.values():
            if c.tem_tipo("tolerante_seca") and not c.perene and c.id not in ja_na_atual:
                adicionar(f"tolerante_seca:{velha.id}->{c.id}", f"Trocar {velha.nome} por {c.nome}", "tolerante_seca", _trocar(atual, pos, c))

    # 3. Uma leguminosa (fixadora de N): na janela vazia ou no lugar de uma cultura que não é a principal
    for c in catalogo.values():
        if not c.tem_tipo("fixadora_n") or c.perene:
            continue
        if (item := na_janela(c)) is not None:
            adicionar(f"leguminosa:janela:{c.id}", f"Plantar {c.nome} no período vazio ({periodo_texto(item.inicio_mes, item.fim_mes, False)})", "leguminosa", atual.itens + (item,))
        if c.id in ja_na_atual:
            continue
        for p, velho in enumerate(atual.itens):
            ja_fixa = velho.cultura_id in catalogo and catalogo[velho.cultura_id].fixa_nitrogenio  # trocar leguminosa por leguminosa não inclui nada
            if p != pos and not velho.perene and velho.cultura_id != c.id and velho.inicio_mes is not None and not ja_fixa:
                adicionar(f"leguminosa:{velho.cultura_id or p}->{c.id}", f"Trocar {_nome_do_item(velho, catalogo)} por {c.nome}", "leguminosa", _trocar(atual, p, c))

    return saida[:MAX_CANDIDATAS]
