"""Texto do 'por que', confiança (a menor das culturas) e lacunas de cada estratégia."""
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.formatos import num
from app.services.motor.modelo import CRITERIOS, Confianca, ItemRotacao, NotaCriterio
from app.services.motor.parametros import DIFERENCA_MINIMA_POR_QUE, MAX_FRASES_POR_QUE, ORDEM_CONFIANCA

FRASES = {
    "agua": "Gasta menos água",
    "terra": "Cuida melhor da terra (cobertura, palha e nitrogênio)",
    "erosao": "Protege mais o solo da erosão",
    "pragas": "Alterna mais as famílias de plantas, o que ajuda contra pragas",
    "renda": "Tem mais culturas para vender",
    "animais": "Dá mais comida para os animais",
}


FRASES_PIORA = {
    "agua": "Usa mais água",
    "terra": "Cuida menos da terra",
    "erosao": "Protege menos o solo da erosão",
    "pragas": "Alterna menos as famílias de plantas",
    "renda": "Tem menos culturas para vender",
    "animais": "Dá menos comida para os animais",
}


def _frases(notas: dict[str, NotaCriterio], atual: dict[str, NotaCriterio], pesos: dict[str, float], textos: dict[str, str], sinal: int) -> list[str]:
    """Até 3 frases dos critérios com diferença de pelo menos 0,1 no sentido `sinal` (+1 ganha, -1 perde), os mais pesados primeiro."""
    achados = []
    for c in CRITERIOS:
        n, a = notas[c].nota, atual[c].nota
        if n is not None and a is not None and sinal * (n - a) >= DIFERENCA_MINIMA_POR_QUE - 1e-9:
            achados.append((sinal * (n - a) * pesos.get(c, 0.0), c, n, a))
    achados.sort(key=lambda g: -g[0])
    return [f"{textos[c]}: nota {num(n)} contra {num(a)} da sua rotação atual." for _, c, n, a in achados[:MAX_FRASES_POR_QUE]]


def por_que(notas: dict[str, NotaCriterio], atual: dict[str, NotaCriterio], pesos: dict[str, float]) -> list[str]:
    """Até 3 frases com os critérios em que a estratégia ganha da atual por pelo menos 0,1, os mais pesados primeiro."""
    return _frases(notas, atual, pesos, FRASES, +1)


def onde_piora(notas: dict[str, NotaCriterio], atual: dict[str, NotaCriterio], pesos: dict[str, float]) -> list[str]:
    """Até 3 frases com os critérios em que a estratégia perde da atual por pelo menos 0,1, os mais pesados primeiro."""
    return _frases(notas, atual, pesos, FRASES_PIORA, -1)


def confianca(itens: tuple[ItemRotacao, ...], catalogo: dict[str, CulturaMotor]) -> tuple[Confianca, list[str]]:
    """A menor `confianca_parametros` entre as culturas da base. Sem nenhuma, ou com valor ausente: baixa, com lacuna."""
    cultura = [catalogo[i.cultura_id] for i in itens if i.cultura_id in catalogo]
    lac: list[str] = []
    niveis = []
    for c in cultura:
        if c.confianca_parametros in ORDEM_CONFIANCA:
            niveis.append(ORDEM_CONFIANCA.index(c.confianca_parametros))
        else:
            niveis.append(0)
            lac.append(f"{c.nome}: confiança dos parâmetros não informada; tratada como baixa.")
    if not niveis:
        return "baixa", ["Nenhuma cultura da rotação está na base: confiança baixa."]
    return ORDEM_CONFIANCA[min(niveis)], lac  # type: ignore[return-value]
