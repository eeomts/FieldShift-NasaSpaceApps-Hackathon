"""Candidatas: a rotação atual mais três regras (janela vazia, troca por tolerante à seca, leguminosa); a janela de semeadura vale pela regra 12."""
from dataclasses import dataclass

from app.services.motor.calendario import maior_janela_vazia, meses_do_periodo, meses_necessarios, meses_para_dias
from app.services.motor.catalogo import CulturaMotor, janela_de_semeadura
from app.services.motor.formatos import periodo_texto
from app.services.motor.modelo import Alerta, Estrategia, ItemRotacao
from app.services.motor.parametros import CEREAIS_INVERNO, MESES_POR_EXTENSO

A_LANCO = "a_lanco_lavoura_em_pe"  # só informação (regra 12): nunca vira sugestão


@dataclass(frozen=True)
class Colocacao:
    """Os itens da rotação com a cultura nova no lugar e os avisos da montagem."""

    itens: tuple[ItemRotacao, ...]
    alertas: tuple[Alerta, ...] = ()


def chave(e: Estrategia) -> frozenset[tuple]:
    """Identidade da estratégia: os mesmos itens (cultura, meses), em qualquer ordem."""
    return frozenset((i.cultura_id, i.inicio_mes, i.fim_mes, i.perene) for i in e.itens)


def _item(c: CulturaMotor, inicio: int, fim: int) -> ItemRotacao:
    return ItemRotacao(c.id, inicio, fim, False, f"{c.nome} ({periodo_texto(inicio, fim, False)})")


def _item_na_janela(c: CulturaMotor, inicio: int, n_janela: int) -> ItemRotacao | None:
    """Cultura plantada em `inicio`, pelo menos o ciclo mínimo (meses inteiros) dentro de `n_janela` meses. None se não couber."""
    if c.perene or c.ciclo_dias_min is None or c.ciclo_dias_min > meses_para_dias(n_janela):
        return None
    n = min(meses_necessarios(c.ciclo_dias_min), n_janela)
    return _item(c, inicio, (inicio - 1 + n - 1) % 12 + 1)


def _nome_do_item(i: ItemRotacao, catalogo: dict[str, CulturaMotor]) -> str:
    return catalogo[i.cultura_id].nome if i.cultura_id in catalogo else i.texto


def _serve_depois_de(condicao: str, x: CulturaMotor) -> bool:
    if condicao == "apos_colheita_graos":
        return x.tem_tipo("comercial") and not x.perene
    if condicao == "apos_cereal_inverno":
        return x.id in CEREAIS_INVERNO
    return False  # apos_silagem: o calendário não diz se foi silagem; a_lanco: só informação


def _anteriores(itens: tuple[ItemRotacao, ...], inicio: int, ignorar: ItemRotacao | None, no_mesmo_mes: bool) -> list[ItemRotacao]:
    """Culturas depois das quais a nova começa: as que terminam no mês antes de `inicio` (e, numa troca, as colhidas no próprio mês)."""
    fins = {(inicio - 2) % 12 + 1, inicio} if no_mesmo_mes else {(inicio - 2) % 12 + 1}
    return [i for i in itens if i is not ignorar and not i.perene and i.inicio_mes is not None and i.fim_mes in fins]


def _cabe_de(c: CulturaMotor, lugar: list[int], m: int) -> bool:
    return c.ciclo_dias_min is None or c.ciclo_dias_min <= meses_para_dias(len(lugar) - lugar.index(m))


def _alerta_colheita(c: CulturaMotor, mes: int, colhendo: list[ItemRotacao], catalogo: dict[str, CulturaMotor]) -> Alerta:
    nomes = " e ".join(dict.fromkeys(_nome_do_item(a, catalogo) for a in colhendo))
    return Alerta("depende_da_colheita", f"{c.nome}: a semeadura é em {MESES_POR_EXTENSO[mes - 1]}, logo depois da colheita de {nomes}; depende da data da sua colheita.")


def _condicao(c: CulturaMotor, condicoes: tuple[str, ...], anteriores: list[ItemRotacao], catalogo: dict[str, CulturaMotor]) -> tuple[Alerta, ...] | None:
    """Regra 12 (a): a cobertura serve depois das culturas anteriores? None = não serve; senão, os avisos."""
    if not condicoes:
        return ()
    validas = [k for k in condicoes if k != A_LANCO]
    if not validas:
        return None  # só a lanço na lavoura em pé: informação, nunca sugestão
    if not anteriores:
        return ()  # campo vazio antes: só a janela decide
    conhecidas = [catalogo[a.cultura_id] for a in anteriores if a.cultura_id in catalogo]
    if any(_serve_depois_de(k, x) for x in conhecidas for k in validas):
        return ()
    fora = [a for a in anteriores if a.cultura_id not in catalogo]
    if fora:
        return (Alerta("janela_nao_confirmada", f"{c.nome}: confira se dá para semear depois de {_nome_do_item(fora[0], catalogo)}."),)
    return None


def _colocar(
    c: CulturaMotor,
    lugar: list[int],
    itens: tuple[ItemRotacao, ...],
    catalogo: dict[str, CulturaMotor],
    estado: str | None,
    ignorar: ItemRotacao | None = None,
    mes_da_colheita: bool = False,
) -> tuple[int, tuple[Alerta, ...]] | None:
    """Regra 12: mês em que a cultura é semeada no `lugar` (meses em ordem) e os avisos; None = não cabe ali.

    Cultura de venda: só a janela de semeadura, se o catálogo tiver uma (sem janela, sem restrição); numa troca, o
    próprio mês da troca tem de estar nela. Cobertura: primeiro mês do lugar que está na janela e em que o ciclo mínimo
    ainda cabe; com `mes_da_colheita` (janela vazia), se nenhum serve, o mês da colheita da anterior, quando a janela
    chega até ele (esse mês não conta no ciclo). Depois, a condição de semeadura (depois de quê).
    """
    j = janela_de_semeadura(c, estado)
    troca = ignorar is not None
    if not c.e_cobertura:
        if j is None:
            return lugar[0], ()
        semeadura = set(meses_do_periodo(j.inicio[0], j.fim[0], False))
        if troca:  # a troca mantém o período da cultura trocada: o mês dela tem de estar na janela
            return (lugar[0], ()) if lugar[0] in semeadura else None
        p = next((m for m in lugar if m in semeadura and _cabe_de(c, lugar, m)), None)
        return None if p is None else (p, ())
    if j is None:
        return lugar[0], (Alerta("janela_nao_confirmada", f"{c.nome}: a época de semeadura ainda não foi confirmada para a sua região."),)
    semeadura = set(meses_do_periodo(j.inicio[0], j.fim[0], False))  # meses inteiros; dá a volta no ano
    anteriores = _anteriores(itens, lugar[0], ignorar, no_mesmo_mes=troca)
    p = next((m for m in lugar if m in semeadura and _cabe_de(c, lugar, m)), None)
    if p is None and mes_da_colheita:
        colheita = (lugar[0] - 2) % 12 + 1
        if colheita in semeadura and any(a.fim_mes == colheita for a in anteriores) and _cabe_de(c, lugar, lugar[0]):
            p = colheita
    if p is None:
        return None
    avisos = _condicao(c, j.condicao_semeadura, anteriores, catalogo)
    if avisos is None:
        return None
    colhendo = [a for a in anteriores if a.fim_mes == p]
    if colhendo:
        avisos += (_alerta_colheita(c, p, colhendo, catalogo),)
    return p, avisos


def _na_janela_vazia(c: CulturaMotor, janela: tuple[int, int], atual: Estrategia, catalogo: dict[str, CulturaMotor], estado: str | None) -> Colocacao | None:
    inicio, n = janela
    if c.perene or c.ciclo_dias_min is None:
        return None
    lugar = [(inicio - 1 + i) % 12 + 1 for i in range(n)]
    achado = _colocar(c, lugar, atual.itens, catalogo, estado, mes_da_colheita=True)
    if achado is None:
        return None
    p, alertas = achado
    if p not in lugar:  # semeada no mês da colheita: o ciclo conta só nos meses vazios
        base = _item_na_janela(c, inicio, n)
        item = None if base is None else _item(c, p, base.fim_mes)
    else:
        item = _item_na_janela(c, p, n - lugar.index(p))
    return None if item is None else Colocacao(atual.itens + (item,), alertas)


def _trocar(atual: Estrategia, pos: int, nova: CulturaMotor) -> tuple[ItemRotacao, ...]:
    velho = atual.itens[pos]
    return atual.itens[:pos] + (_item(nova, velho.inicio_mes, velho.fim_mes),) + atual.itens[pos + 1 :]


def _trocar_por(atual: Estrategia, pos: int, nova: CulturaMotor, catalogo: dict[str, CulturaMotor], estado: str | None) -> Colocacao | None:
    velho = atual.itens[pos]
    lugar = velho.meses()
    if not lugar:
        return Colocacao(_trocar(atual, pos, nova))
    achado = _colocar(nova, lugar, atual.itens, catalogo, estado, ignorar=velho)
    if achado is None:
        return None
    p, alertas = achado
    if p == lugar[0]:
        return Colocacao(_trocar(atual, pos, nova), alertas)
    item = _item(nova, p, velho.fim_mes)  # empurrada para o início da janela de semeadura
    return Colocacao(atual.itens[:pos] + (item,) + atual.itens[pos + 1 :], alertas)


def _principal(atual: tuple[ItemRotacao, ...], catalogo: dict[str, CulturaMotor]) -> int | None:
    """Posição da cultura principal: a comercial de ciclo mais longo (ciclo máximo) entre as da rotação atual."""
    achados = [
        (catalogo[i.cultura_id].ciclo_dias_max, -pos)
        for pos, i in enumerate(atual)
        if i.cultura_id in catalogo and catalogo[i.cultura_id].tem_tipo("comercial") and catalogo[i.cultura_id].ciclo_dias_max
    ]
    return None if not achados else -max(achados)[1]


def _nome_na_janela(c: CulturaMotor, col: Colocacao, janela: tuple[int, int]) -> str:
    """Nome da candidata de janela. Semeada no mês da colheita (antes do período vazio): "logo depois da colheita"."""
    novo = col.itens[-1]
    inicio, n = janela
    onde = "logo depois da colheita" if (novo.inicio_mes - inicio) % 12 >= n else "no período vazio"
    return f"Plantar {c.nome} {onde} ({periodo_texto(novo.inicio_mes, novo.fim_mes, False)})"


def gerar_candidatas(atual: Estrategia, catalogo: dict[str, CulturaMotor], meses_vazios: list[int], estado: str | None = None) -> list[Estrategia]:
    """Candidatas sem repetir itens e sem a atual, todas (sem corte; ordem: janela, tolerante à seca, leguminosa).

    Só entram culturas válidas no `estado` da fazenda (regra 13); as da atual continuam no catálogo para as contas.
    A janela de semeadura e a cultura anterior decidem onde a cultura nova entra (regra 12).
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

    # 1. Janela vazia: cada cultura cujo ciclo mínimo cabe na maior janela contínua
    for c in novas:
        if (col := na_janela(c)) is not None:
            adicionar(f"janela:{c.id}", _nome_na_janela(c, col, janela), "janela", col)

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
            adicionar(f"leguminosa:janela:{c.id}", _nome_na_janela(c, col, janela), "leguminosa", col)
        if c.id in ja_na_atual:
            continue
        for p, velho in enumerate(atual.itens):
            ja_fixa = velho.cultura_id in catalogo and catalogo[velho.cultura_id].fixa_nitrogenio  # trocar leguminosa por leguminosa não inclui nada
            if p != pos and not velho.perene and velho.cultura_id != c.id and velho.inicio_mes is not None and not ja_fixa:
                if (col := _trocar_por(atual, p, c, catalogo, estado)) is not None:
                    adicionar(f"leguminosa:{velho.cultura_id or p}->{c.id}", f"Trocar {_nome_do_item(velho, catalogo)} por {c.nome}", "leguminosa", col)

    return saida
