"""Fusão de evidências do solo (MOTOR-DE-ANALISE.md, cálculo 2): textura, matéria orgânica e acidez, cada fonte com seu peso."""
from app.schemas.solo import AtributoSolo, EvidenciaSolo, SoloPonto
from app.services.solo import derivados

# Peso por fonte (MOTOR-DE-ANALISE.md, cálculo 2; proposta inicial). "Não sei" pesa 0: não gera evidência.
PESO_POR_FONTE = {"laudo": 0.9, "teste_campo": 0.7, "produtor": 0.5, "soilgrids": 0.4}
# Confiança pela soma dos pesos do valor vencedor (proposta do coordenador, validar com agronomia).
SOMA_CONFIANCA_ALTA = 0.9  # e nenhuma evidência a favor de outro valor
SOMA_CONFIANCA_MEDIA = 0.5
FONTES_DO_PRODUTOR = ("produtor", "teste_campo")  # o que a pessoa viu ou testou no campo (o laudo é medida)

ATRIBUTOS = ("textura", "materia_organica", "acidez")
VALORES = {
    "textura": ("arenosa", "media", "argilosa"),
    "materia_organica": ("baixa", "media", "alta"),
    "acidez": ("alta", "media", "adequada", "alcalino"),
}
# Como o valor aparece na frase de divergência.
ROTULOS = {
    "textura": {"arenosa": "terra arenosa", "media": "terra de textura média", "argilosa": "terra argilosa"},
    "materia_organica": {"baixa": "pouca matéria orgânica", "media": "matéria orgânica média", "alta": "bastante matéria orgânica"},
    "acidez": {"alta": "solo ácido", "media": "acidez média", "adequada": "acidez adequada", "alcalino": "solo alcalino"},
}
FRASE_DIVERGENCIA = "O mapa global sugere {mapa}, mas você observou {produtor}. No seu campo vale o que você vê."


def _do_produtor(retrato: dict) -> list[tuple[str, EvidenciaSolo]]:
    """(atributo, evidência) do que o produtor contou: laudo, indicadores e figuras da pergunta 19."""
    itens: list[tuple[str, EvidenciaSolo]] = []

    def somar(atributo: str, valor: str, fonte: str, texto: str) -> None:
        if atributo in ATRIBUTOS and valor in VALORES[atributo] and fonte in PESO_POR_FONTE:
            itens.append((atributo, EvidenciaSolo(fonte=fonte, valor=valor, peso=PESO_POR_FONTE[fonte], texto=texto)))

    for i in retrato.get("indicadores") or []:
        somar(i.get("atributo"), i.get("valor"), i.get("fonte"), i.get("texto") or "")
    figuras = retrato.get("figuras") or {}
    for i in figuras.get("atributos") or []:
        rotulo = {"q19_cor": f"Cor da terra: {figuras.get('cor')}", "q19_jeito": f"Jeito da terra na mão: {figuras.get('jeito')}"}
        somar(i.get("atributo"), i.get("valor"), "produtor", rotulo.get(i.get("origem"), "Figuras da pergunta 19"))
    return itens


def _do_mapa(solo: SoloPonto | None) -> list[tuple[str, EvidenciaSolo]]:
    if solo is None or solo.sem_dado:
        return []
    peso = PESO_POR_FONTE["soilgrids"]
    itens: list[tuple[str, EvidenciaSolo]] = []
    textura = derivados.textura_simples(solo.classe_textural)
    if textura is not None:
        texto = f"Mapa global: {solo.argila_pct:g}% de argila, {solo.areia_pct:g}% de areia e {solo.silte_pct:g}% de silte (0–30 cm)"
        itens.append(("textura", EvidenciaSolo(fonte="soilgrids", valor=textura, peso=peso, texto=texto)))
    mo = derivados.classe_materia_organica(solo.materia_organica_g_kg, solo.densidade_g_cm3)
    if mo is not None:
        texto = f"Mapa global: {solo.materia_organica_g_kg:g} g/kg de matéria orgânica (0–30 cm)"
        itens.append(("materia_organica", EvidenciaSolo(fonte="soilgrids", valor=mo, peso=peso, texto=texto)))
    acidez = derivados.classe_acidez(solo.ph)
    if acidez is not None:
        itens.append(("acidez", EvidenciaSolo(fonte="soilgrids", valor=acidez, peso=peso, texto=f"Mapa global: pH {solo.ph:g} em água (0–30 cm)")))
    return itens


def _soma_por_valor(evidencias: list[EvidenciaSolo]) -> dict[str, float]:
    somas: dict[str, float] = {}
    for e in evidencias:
        somas[e.valor] = somas.get(e.valor, 0.0) + e.peso
    return somas


def _vencedor(evidencias: list[EvidenciaSolo]) -> str:
    """Maior soma de pesos; empate: a evidência individual mais pesada, depois a que apareceu primeiro."""
    somas = _soma_por_valor(evidencias)
    maior_peso = {v: max(e.peso for e in evidencias if e.valor == v) for v in somas}
    return max(somas, key=lambda v: (round(somas[v], 6), maior_peso[v]))  # max devolve o primeiro em empate total


def fundir(atributo: str, evidencias: list[EvidenciaSolo]) -> AtributoSolo:
    """Valor, confiança e divergência de um atributo. Sem evidência: valor e confiança nulos."""
    if not evidencias:
        return AtributoSolo(atributo=atributo)
    ordenadas = sorted(evidencias, key=lambda e: -e.peso)  # estável: empate mantém a ordem de chegada
    laudo = [e for e in evidencias if e.fonte == "laudo"]
    if laudo:
        # O laudo é medida de laboratório: decide sozinho (SOILGRIDS.md: "substitui o SoilGrids e a confiança passa a alta").
        return AtributoSolo(atributo=atributo, valor=laudo[0].valor, confianca="alta", evidencias=ordenadas)
    valor = _vencedor(evidencias)
    somas = _soma_por_valor(evidencias)
    soma = round(somas[valor], 6)
    if soma >= SOMA_CONFIANCA_ALTA and len(somas) == 1:
        confianca = "alta"
    elif soma >= SOMA_CONFIANCA_MEDIA:
        confianca = "media"
    else:
        confianca = "baixa"
    return AtributoSolo(atributo=atributo, valor=valor, confianca=confianca, evidencias=ordenadas, divergencia=_divergencia(atributo, evidencias))


def _divergencia(atributo: str, evidencias: list[EvidenciaSolo]) -> str | None:
    """A frase de aviso quando o mapa global discorda do que o produtor observou."""
    mapa = [e for e in evidencias if e.fonte == "soilgrids"]
    produtor = [e for e in evidencias if e.fonte in FONTES_DO_PRODUTOR]
    if not mapa or not produtor:
        return None
    valor_produtor = _vencedor(produtor)
    if mapa[0].valor == valor_produtor:
        return None
    rotulos = ROTULOS[atributo]
    return FRASE_DIVERGENCIA.format(mapa=rotulos[mapa[0].valor], produtor=rotulos[valor_produtor])


def sintese(retrato_do_produtor: dict, solo: SoloPonto | None) -> list[AtributoSolo]:
    """Os três atributos fundidos, sempre na mesma ordem (textura, matéria orgânica, acidez)."""
    todas = _do_produtor(retrato_do_produtor) + _do_mapa(solo)
    return [fundir(a, [e for atributo, e in todas if atributo == a]) for a in ATRIBUTOS]
