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

_SNS_SOLO = {
    # chave: (atributo, texto se "sim", texto se "não")
    "q14_encharca": ("drenagem", "Água fica empoçada mais de um dia", "Água não fica empoçada"),
    "q15_casca": ("encrostamento", "Forma casca quando seca", "Não forma casca"),
    "q16_erosao": ("erosao_observada", "Já viu a chuva levando terra", "Não viu a chuva levando terra"),
    "q17_dura": ("compactacao", "Terra muito dura para cavar ou arar", "Terra não é dura demais"),
    "q18_minhocas": ("vida_no_solo", "Encontra minhocas", "Não encontra minhocas"),
    "q20_partes_piores": ("variacao_no_campo", "Tem partes onde a lavoura vai pior", "Lavoura uniforme"),
    "q21_calcario": ("calcario", "Já usou calcário", "Nunca usou calcário"),
    "q22_adubo": ("adubacao", "Usa adubo ou esterco", "Não usa adubo nem esterco"),
    "q11_palha": ("palhada", "Deixa a palha no campo", "Não deixa a palha no campo"),
}
_TEXTURA = {"arenosa": "Mais arenosa", "media": "Meio-termo", "argilosa": "Mais argilosa"}


def retrato_solo(r: Respostas) -> dict:
    """Retrato provisório do solo. Tudo marcado como 'informado pelo produtor'."""
    indicadores = []
    if _respondida(r.q13_textura):
        indicadores.append({"atributo": "textura", "valor": _TEXTURA[r.q13_textura], "confianca": "media"})
    for chave, (atributo, se_sim, se_nao) in _SNS_SOLO.items():
        v = getattr(r, chave)
        if v in ("sim", "nao"):
            indicadores.append({"atributo": atributo, "valor": se_sim if v == "sim" else se_nao, "confianca": "media"})

    figuras = None
    cor, jeito = r.q19_cor, r.q19_jeito
    if _respondida(cor) and _respondida(jeito):
        leitura, conf = _CRUZAMENTO.get((cor, jeito), (f"{_COR[cor].capitalize()}; {_JEITO[jeito]}", "baixa"))
        figuras = {"cor": cor, "jeito": jeito, "leitura": leitura, "confianca": conf}
    elif _respondida(cor):
        figuras = {"cor": cor, "jeito": None, "leitura": _COR[cor].capitalize(), "confianca": "baixa"}
    elif _respondida(jeito):
        figuras = {"cor": None, "jeito": jeito, "leitura": _JEITO[jeito].capitalize(), "confianca": "baixa"}

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
