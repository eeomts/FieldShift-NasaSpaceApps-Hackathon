"""Pesos das prioridades, nota final por soma ponderada e escolha das duas melhores."""
from app.services.motor.candidatas import chave
from app.services.motor.modelo import CRITERIOS, NotaCriterio, ResultadoEstrategia
from app.services.motor.parametros import MAX_MELHORES, PESO_NAO_ESCOLHIDO, PESOS_PRIORIDADE


def pesos_das_prioridades(prioridades: list[str]) -> dict[str, float]:
    """Até 3 prioridades valem 0,5 / 0,3 / 0,2 reescalados para somar 1 - 0,05 x (não escolhidos); os demais valem 0,05.

    Sem prioridade: 1/6 para cada critério. Repetida ou desconhecida é ignorada.
    """
    escolhidas = [p for p in dict.fromkeys(prioridades) if p in CRITERIOS][: len(PESOS_PRIORIDADE)]
    if not escolhidas:
        return {c: 1 / len(CRITERIOS) for c in CRITERIOS}
    base = PESOS_PRIORIDADE[: len(escolhidas)]
    alvo = 1 - PESO_NAO_ESCOLHIDO * (len(CRITERIOS) - len(escolhidas))
    pesos = {c: PESO_NAO_ESCOLHIDO for c in CRITERIOS}
    for criterio, peso in zip(escolhidas, base):
        pesos[criterio] = peso / sum(base) * alvo
    return pesos


def nota_final(notas: dict[str, NotaCriterio], pesos: dict[str, float]) -> tuple[float | None, dict[str, float]]:
    """Soma ponderada só dos critérios com nota; o peso dos sem dado vai, na mesma proporção, para os outros.

    Devolve (nota, pesos efetivos). Nenhum critério com dado: (None, {}).
    """
    validos = {c: pesos[c] for c in CRITERIOS if notas[c].nota is not None}
    total = sum(validos.values())
    if not validos or total <= 0:
        return None, {}
    efetivos = {c: p / total for c, p in validos.items()}
    return round(sum(notas[c].nota * p for c, p in efetivos.items()), 4), efetivos


def _chave(r: ResultadoEstrategia) -> tuple:
    """Maior nota final; empate: maior nota em terra, depois menos alertas."""
    terra = r.notas["terra"].nota
    return (-(r.nota_final if r.nota_final is not None else -1), -(terra if terra is not None else -1), len(r.alertas))


def ordenar(resultados: list[ResultadoEstrategia]) -> list[ResultadoEstrategia]:
    return sorted(resultados, key=_chave)


def melhores(atual: ResultadoEstrategia, candidatas: list[ResultadoEstrategia], n: int = MAX_MELHORES) -> list[ResultadoEstrategia]:
    """As `n` melhores diferentes da atual e entre si (mesmos itens = mesma estratégia)."""
    vistos = {chave(atual.estrategia)}
    saida = []
    for r in ordenar(candidatas):
        if chave(r.estrategia) not in vistos:
            vistos.add(chave(r.estrategia))
            saida.append(r)
        if len(saida) == n:
            break
    return saida
