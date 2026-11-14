"""Regras que transformam as respostas nas saídas do questionário (ONBOARDING.md, "O que sai")."""
from app.onboarding.schemas import ItemCalendario, Respostas

# Perguntas de OBSERVAÇÃO do solo. As de manejo (q12 análise, q21 calcário, q22 adubo) não contam:
# responder "não usei calcário" não diz nada sobre como o solo é.
_OBSERVACAO = ["q13_textura", "q14_encharca", "q15_casca", "q16_erosao", "q17_dura",
               "q18_minhocas", "q20_partes_piores"]
# 8 observações possíveis (as 7 acima + a pergunta 19, que vale uma quando tem cor e jeito)
MIN_OBSERVACOES_B = 5


def _respondida(valor) -> bool:
    return valor is not None and valor != "nao_sei"


def calcula_papel(r: Respostas) -> str:
    """Quem está respondendo. É independente do perfil: um técnico pode ter laudo (C) ou não (A/B)."""
    return "tecnico" if r.q1_quem == "tecnico" else "produtor"


def calcula_perfil(r: Respostas) -> str:
    """Nível de dado sobre o solo (ONBOARDING.md): A experiência, B observador, C com laudo."""
    if r.q12_analise == "sim" and r.q12_tem_resultado == "sim":
        return "C"
    observacoes = sum(_respondida(getattr(r, k)) for k in _OBSERVACAO)
    observacoes += _respondida(r.q19_cor) and _respondida(r.q19_jeito)
    if _respondida(r.q13_textura) or observacoes >= MIN_OBSERVACOES_B:
        return "B"
    return "A"


def meses_ocupados(item: ItemCalendario) -> set[int]:
    if item.perene:
        return set(range(1, 13))
    if item.inicio_mes is None or item.fim_mes is None:
        return set()
    if item.inicio_mes <= item.fim_mes:
        return set(range(item.inicio_mes, item.fim_mes + 1))
    return set(range(item.inicio_mes, 13)) | set(range(1, item.fim_mes + 1))


def meses_sem_cobertura(itens: list[ItemCalendario]) -> list[int]:
    if not itens:
        return []
    ocupados = set().union(*(meses_ocupados(i) for i in itens))
    return [m for m in range(1, 13) if m not in ocupados]


# Leitura de cada rodada da pergunta 19 (faixas preliminares, [verificar com pedologia]).
_COR = {
    "escura": "mais matéria orgânica",
    "marrom": "matéria orgânica média",
    "vermelha": "geralmente bem drenada",
    "amarela": "drenagem um pouco menor",
    "cinza": "fica encharcada com frequência",
    "clara": "pouca matéria orgânica; pode ser arenosa",
}
_JEITO = {
    "solta": "arenosa; retém pouca água",
    "fofa": "boa estrutura e vida no solo",
    "gruda": "argilosa",
    "torroes": "compactada ou adensada",
    "racha": "argila expansiva",
    "pedras": "pedregosa; raiz e máquina têm limite",
}
_CRUZAMENTO = {
    ("escura", "fofa"): ("Matéria orgânica boa, estrutura boa", "media"),
    ("vermelha", "gruda"): ("Argilosa e bem drenada", "media"),
    ("cinza", "gruda"): ("Argilosa com drenagem ruim; cuidado com culturas sensíveis a encharcamento", "media"),
    ("clara", "solta"): ("Arenosa, pouca matéria orgânica, seca rápido", "media"),
    ("escura", "solta"): ("Combinação incomum; vale confirmar com o teste do tato", "baixa"),
}

# Atributos padronizados que cada figura indica (o motor de análise cruza com o SoilGrids).
_COR_ATRIBUTOS = {
    "escura": [("materia_organica", "alta")],
    "marrom": [("materia_organica", "media")],
    "vermelha": [("drenagem", "boa")],
    "amarela": [("drenagem", "moderada")],
    "cinza": [("drenagem", "ruim")],
    "clara": [("materia_organica", "baixa")],
}
_JEITO_ATRIBUTOS = {
    "solta": [("textura", "arenosa")],
    "fofa": [("estrutura", "boa")],
    "gruda": [("textura", "argilosa")],
    "torroes": [("compactacao", "presente")],
    "racha": [("textura", "argilosa"), ("argila_expansiva", "presente")],
    "pedras": [("pedregosidade", "presente")],
}

# Perguntas sim/não do solo.
# chave: (atributo, valor se "sim", valor se "não", texto se "sim", texto se "não")
# O VALOR é a categoria que o motor usa nas contas; o TEXTO é só para mostrar na tela.
_SNS_SOLO = {
    "q14_encharca": ("drenagem", "ruim", "boa", "Água fica empoçada mais de um dia", "Água não fica empoçada"),
    "q15_casca": ("encrostamento", "presente", "ausente", "Forma casca quando seca", "Não forma casca"),
    "q16_erosao": ("erosao_observada", "sim", "nao", "Já viu a chuva levando terra", "Não viu a chuva levando terra"),
    "q17_dura": ("compactacao", "presente", "ausente", "Terra muito dura para cavar ou arar", "Terra não é dura demais"),
    "q18_minhocas": ("vida_no_solo", "boa", "baixa", "Encontra minhocas", "Não encontra minhocas"),
    "q20_partes_piores": ("variacao_no_campo", "sim", "nao", "Tem partes onde a lavoura vai pior", "Lavoura uniforme"),
    "q21_calcario": ("calcario", "sim", "nao", "Já usou calcário", "Nunca usou calcário"),
    "q22_adubo": ("adubacao", "sim", "nao", "Usa adubo ou esterco", "Não usa adubo nem esterco"),
    "q11_palha": ("palhada", "sim", "nao", "Deixa a palha no campo", "Não deixa a palha no campo"),
}
_TEXTURA = {"arenosa": "Mais arenosa", "media": "Meio-termo", "argilosa": "Mais argilosa"}


def _indicador(atributo: str, valor: str, origem: str, confianca: str, texto: str | None = None,
               fonte: str = "produtor") -> dict:
    return {"atributo": atributo, "valor": valor, "texto": texto, "fonte": fonte, "origem": origem,
            "confianca": confianca}


def retrato_solo(r: Respostas) -> dict:
    """Retrato provisório do solo, com valores padronizados para o motor de análise.

    - indicadores: o que o produtor respondeu (sim/não e textura), com valor padronizado e texto de tela;
    - figuras: a leitura da pergunta 19 e os atributos padronizados que ela indica (confiança baixa).
    """
    indicadores = []
    if _respondida(r.q13_textura):
        indicadores.append(_indicador("textura", r.q13_textura, "q13_textura", "media", _TEXTURA[r.q13_textura]))
    for chave, (atributo, v_sim, v_nao, t_sim, t_nao) in _SNS_SOLO.items():
        v = getattr(r, chave)
        if v in ("sim", "nao"):
            sim = v == "sim"
            indicadores.append(_indicador(atributo, v_sim if sim else v_nao, chave, "media", t_sim if sim else t_nao))

    figuras = None
    cor = r.q19_cor if _respondida(r.q19_cor) else None
    jeito = r.q19_jeito if _respondida(r.q19_jeito) else None
    if cor or jeito:
        if cor and jeito:
            leitura, conf = _CRUZAMENTO.get((cor, jeito), (f"{_COR[cor].capitalize()}; {_JEITO[jeito]}", "baixa"))
        else:
            leitura, conf = (_COR[cor] if cor else _JEITO[jeito]).capitalize(), "baixa"
        atributos = [_indicador(a, v, "q19_cor", "baixa") for a, v in _COR_ATRIBUTOS.get(cor, [])]
        atributos += [_indicador(a, v, "q19_jeito", "baixa") for a, v in _JEITO_ATRIBUTOS.get(jeito, [])]
        figuras = {"cor": cor, "jeito": jeito, "leitura": leitura, "confianca": conf, "atributos": atributos}

    return {"fonte": "produtor", "indicadores": indicadores, "figuras": figuras}


def proximos_passos(r: Respostas) -> list[dict]:
    """Sugestões simples a partir dos 'não sei' (no máximo 3)."""
    passos = []
    if r.q13_textura in (None, "nao_sei"):
        passos.append({"id": "teste_tato", "titulo": "Teste do tato (2 minutos)",
                       "texto": "Molhe um punhado de terra e aperte. Se esfarela, é arenosa; se molda e gruda, é argilosa."})
    if r.q12_analise in ("nao", "nao_sei"):
        passos.append({"id": "analise_solo", "titulo": "Análise de solo",
                       "texto": "Uma análise em laboratório deixa a comparação de estratégias bem mais confiável."})
    if r.q18_minhocas == "nao_sei":
        passos.append({"id": "buraco_20cm", "titulo": "Olhe a vida no solo",
                       "texto": "Cave um buraco de um palmo depois de uma chuva e conte as minhocas."})
    if r.q14_encharca == "nao_sei":
        passos.append({"id": "observar_chuva", "titulo": "Observe depois da próxima chuva",
                       "texto": "Veja se a água fica parada no campo por mais de um dia."})
    if r.q19_cor in (None, "nao_sei") or r.q19_jeito in (None, "nao_sei"):
        passos.append({"id": "punhado", "titulo": "Pegue um punhado de terra",
                       "texto": "Compare a cor e o jeito na mão com as figuras do questionário."})
    return passos[:3]
