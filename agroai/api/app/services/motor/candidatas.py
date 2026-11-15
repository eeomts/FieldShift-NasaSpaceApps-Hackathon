"""Candidatas: a rotação atual mais três regras (janela vazia, troca por tolerante à seca, leguminosa)."""
from calendar import monthrange

from app.services.motor.calendario import maior_janela_vazia, meses_necessarios, meses_para_dias
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.formatos import periodo_texto
from app.services.motor.modelo import Estrategia, ItemRotacao
from app.services.motor.parametros import CEREAIS_INVERNO, MAX_CANDIDATAS

# Valores de `condicao_semeadura` que o motor entende (regra 12); outro valor vira lacuna, nunca sugestão firme
APOS_COLHEITA_GRAOS = "apos_colheita_graos"
APOS_CEREAL_INVERNO = "apos_cereal_inverno"
APOS_SILAGEM = "apos_silagem"
A_LANCO_EM_PE = "a_lanco_lavoura_em_pe"
CONDICOES_VERIFICAVEIS = (APOS_COLHEITA_GRAOS, APOS_CEREAL_INVERNO)


def chave(e: Estrategia) -> frozenset[tuple]:
    """Identidade da estratégia: os mesmos itens (cultura, meses), em qualquer ordem."""
    return frozenset((i.cultura_id, i.inicio_mes, i.fim_mes, i.perene) for i in e.itens)


def _dia_do_ano(mm_dd: str) -> int:
    mes, dia = (int(x) for x in mm_dd.split("-"))
    return sum(monthrange(2001, m)[1] for m in range(1, mes)) + dia  # ano sem 29/02


def _mes_na_janela_de_semeadura(c: CulturaMotor, mes: int) -> bool | None:
    """O mês tem algum dia dentro da janela de semeadura da cultura (que pode virar o ano)? None: sem janela legível."""
    if not c.semeadura_inicio or not c.semeadura_fim:
        return None
    try:
        ini, fim = _dia_do_ano(c.semeadura_inicio), _dia_do_ano(c.semeadura_fim)
        primeiro = _dia_do_ano(f"{mes:02d}-01")
        ultimo = primeiro + monthrange(2001, mes)[1] - 1
    except (ValueError, IndexError):
        return None
    return (ini <= ultimo and fim >= primeiro) if ini <= fim else (ultimo >= ini or primeiro <= fim)


def _lacuna_sem_janela(c: CulturaMotor) -> str:
    return f"{c.nome}: ainda não confirmamos a melhor época para semear esta cobertura. Confirme com seu agrônomo."


def _lacuna_sem_cultura_anterior(c: CulturaMotor) -> str:
    return f"{c.nome}: não conseguimos confirmar depois de qual cultura esta cobertura pode ser semeada. Confirme com seu agrônomo."


def _lacuna_silagem(c: CulturaMotor) -> str:
    return f"{c.nome}: esta cobertura só serve depois de uma cultura colhida para silagem, e não sabemos se a sua é. Confirme antes de semear."


def _condicao_semeadura(c: CulturaMotor, anteriores: list[ItemRotacao], catalogo: dict[str, CulturaMotor]) -> list[str] | None:
    """Lacunas da condição de semeadura depois das culturas `anteriores`; None se a condição não é atendida (não gera)."""
    codigos = [t for t in (c.condicao_semeadura or "").split("|") if t]
    if codigos and all(t == A_LANCO_EM_PE for t in codigos):
        return None  # a lanço na lavoura em pé: só informação, nunca sugestão
    codigos = [t for t in codigos if t != A_LANCO_EM_PE]
    if not codigos:
        return [_lacuna_sem_cultura_anterior(c)]  # janela sem condição no catálogo: não dá para confirmar
    conhecidas = [catalogo[i.cultura_id] for i in anteriores if i.cultura_id in catalogo]
    for a in conhecidas:
        if (APOS_COLHEITA_GRAOS in codigos and a.tem_tipo("comercial")) or (APOS_CEREAL_INVERNO in codigos and a.id in CEREAIS_INVERNO):
            return []
    if not anteriores or len(conhecidas) < len(anteriores):
        return [_lacuna_sem_cultura_anterior(c)]  # sem cultura anterior conhecida (fora do catálogo ou rotação vazia)
    if APOS_SILAGEM in codigos:
        return [_lacuna_silagem(c)]  # não sabemos se a anterior foi colhida como silagem
    if any(t not in CONDICOES_VERIFICAVEIS for t in codigos):
        return [_lacuna_sem_cultura_anterior(c)]  # valor que o motor não conhece: conservador
    return None


def _lacunas_da_cobertura(c: CulturaMotor, mes: int | None, anteriores: list[ItemRotacao], catalogo: dict[str, CulturaMotor]) -> list[str] | None:
    """Regra 12 para a cobertura semeada em `mes`: None se não pode ser sugerida; senão, as lacunas (vazio = tudo confirmado).

    Só vale para quem não é `comercial` (grão não tem janela de recomendação no catálogo).
    """
    if c.tem_tipo("comercial"):
        return []
    na_janela = None if mes is None else _mes_na_janela_de_semeadura(c, mes)
    if na_janela is False:
        return None
    sem_janela = [_lacuna_sem_janela(c)] if na_janela is None else []
    if c.semeadura_inicio is None and c.semeadura_fim is None and not c.condicao_semeadura:
        return sem_janela  # catálogo sem janela nem condição: segue como antes, só com a lacuna
    cond = _condicao_semeadura(c, anteriores, catalogo)
    return None if cond is None else sem_janela + cond


def _terminam_antes(atual: tuple[ItemRotacao, ...], mes: int, ignorar: int | None = None, no_mesmo_mes: bool = False) -> list[ItemRotacao]:
    """Itens da rotação atual que terminam no mês anterior a `mes` (as culturas depois das quais a nova começa).

    `no_mesmo_mes`: conta também quem termina em `mes` (troca de uma cultura que começa quando a anterior é colhida, como a safrinha).
    """
    fins = {(mes - 2) % 12 + 1, mes} if no_mesmo_mes else {(mes - 2) % 12 + 1}
    return [i for p, i in enumerate(atual) if p != ignorar and not i.perene and i.inicio_mes is not None and i.fim_mes in fins]


def _item_na_janela(
    c: CulturaMotor, inicio: int, n_janela: int, atual: tuple[ItemRotacao, ...] = (), catalogo: dict[str, CulturaMotor] | None = None
) -> tuple[ItemRotacao, list[str]] | None:
    """Cultura plantada na janela vazia, pelo menos o ciclo mínimo (meses inteiros), e as lacunas da regra 12.

    Começa no primeiro mês da janela que cai na janela de semeadura da cobertura e em que o ciclo mínimo ainda cabe
    até o fim da janela vazia. None se não houver mês assim.
    """
    if c.perene or c.ciclo_dias_min is None:
        return None
    catalogo = catalogo if catalogo is not None else {}
    anteriores = _terminam_antes(atual, inicio)
    for k in range(n_janela):
        if c.ciclo_dias_min > meses_para_dias(n_janela - k):
            return None  # os próximos meses restam ainda menos
        mes = (inicio - 1 + k) % 12 + 1
        lacunas = _lacunas_da_cobertura(c, mes, anteriores, catalogo)
        if lacunas is None:
            if _mes_na_janela_de_semeadura(c, mes) is False:
                continue  # ainda não é época de semear: tenta o mês seguinte
            return None  # a condição não é atendida em mês nenhum
        n = min(meses_necessarios(c.ciclo_dias_min), n_janela - k)
        fim = (mes - 1 + n - 1) % 12 + 1
        return ItemRotacao(c.id, mes, fim, False, f"{c.nome} ({periodo_texto(mes, fim, False)})"), lacunas
    return None


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


def _lacunas_da_troca(atual: Estrategia, pos: int, nova: CulturaMotor, catalogo: dict[str, CulturaMotor]) -> list[str] | None:
    """Regra 12 na troca: a cobertura passa a ser semeada no início do período da cultura trocada, depois da que a antecede."""
    velho = atual.itens[pos]
    if velho.inicio_mes is None:
        return _lacunas_da_cobertura(nova, None, [], catalogo)
    return _lacunas_da_cobertura(nova, velho.inicio_mes, _terminam_antes(atual.itens, velho.inicio_mes, ignorar=pos, no_mesmo_mes=True), catalogo)


def _nome_do_item(i: ItemRotacao, catalogo: dict[str, CulturaMotor]) -> str:
    return catalogo[i.cultura_id].nome if i.cultura_id in catalogo else i.texto


def gerar_candidatas(atual: Estrategia, catalogo: dict[str, CulturaMotor], meses_vazios: list[int], estado: str | None = None) -> list[Estrategia]:
    """Candidatas sem repetir itens e sem a atual, no máximo MAX_CANDIDATAS (ordem: janela, tolerante à seca, leguminosa).

    Só entram culturas válidas no `estado` da fazenda (regra 13); as da atual continuam no catálogo para as contas.
    """
    novas = [c for c in catalogo.values() if c.vale_em(estado)]
    vistos = {chave(atual)}
    saida: list[Estrategia] = []

    def adicionar(id_: str, nome: str, origem: str, itens: tuple[ItemRotacao, ...], lacunas: list[str] | None = None) -> None:
        e = Estrategia(id_, nome, origem, itens, tuple(lacunas or ()))  # type: ignore[arg-type]
        if chave(e) not in vistos:
            vistos.add(chave(e))
            saida.append(e)

    ja_na_atual = {i.cultura_id for i in atual.itens}
    janela = maior_janela_vazia(meses_vazios)

    def na_janela(c: CulturaMotor) -> tuple[ItemRotacao, list[str]] | None:
        return None if janela is None else _item_na_janela(c, *janela, atual.itens, catalogo)

    def na_troca(pos: int, nova: CulturaMotor) -> list[str] | None:
        return _lacunas_da_troca(atual, pos, nova, catalogo)

    # 1. Janela vazia: cada cultura cujo ciclo mínimo cabe na maior janela contínua
    for c in novas:
        if (achado := na_janela(c)) is not None:
            item, lacunas = achado
            adicionar(f"janela:{c.id}", f"Plantar {c.nome} no período vazio ({periodo_texto(item.inicio_mes, item.fim_mes, False)})", "janela", atual.itens + (item,), lacunas)

    # 2. A principal trocada por cada cultura tolerante à seca, no mesmo período
    pos = _principal(atual.itens, catalogo)
    if pos is not None and not atual.itens[pos].perene:
        velha = catalogo[atual.itens[pos].cultura_id]
        for c in novas:
            if c.tem_tipo("tolerante_seca") and not c.perene and c.id not in ja_na_atual and (lacunas := na_troca(pos, c)) is not None:
                adicionar(f"tolerante_seca:{velha.id}->{c.id}", f"Trocar {velha.nome} por {c.nome}", "tolerante_seca", _trocar(atual, pos, c), lacunas)

    # 3. Uma leguminosa (fixadora de N): na janela vazia ou no lugar de uma cultura que não é a principal
    for c in novas:
        if not c.tem_tipo("fixadora_n") or c.perene:
            continue
        if (achado := na_janela(c)) is not None:
            item, lacunas = achado
            adicionar(f"leguminosa:janela:{c.id}", f"Plantar {c.nome} no período vazio ({periodo_texto(item.inicio_mes, item.fim_mes, False)})", "leguminosa", atual.itens + (item,), lacunas)
        if c.id in ja_na_atual:
            continue
        for p, velho in enumerate(atual.itens):
            ja_fixa = velho.cultura_id in catalogo and catalogo[velho.cultura_id].fixa_nitrogenio  # trocar leguminosa por leguminosa não inclui nada
            if p != pos and not velho.perene and velho.cultura_id != c.id and velho.inicio_mes is not None and not ja_fixa and (lacunas := na_troca(p, c)) is not None:
                adicionar(f"leguminosa:{velho.cultura_id or p}->{c.id}", f"Trocar {_nome_do_item(velho, catalogo)} por {c.nome}", "leguminosa", _trocar(atual, p, c), lacunas)

    return saida[:MAX_CANDIDATAS]
