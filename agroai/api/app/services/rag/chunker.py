"""Divide markdown em trechos por seção (#, ## e ###), com o caminho dos títulos em cada trecho."""
import re
from dataclasses import dataclass

TITULO = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
CERCA_CODIGO = re.compile(r"^\s*(```|~~~)")

MAX_CARACTERES = 1800  # ~450 tokens em português
MIN_CARACTERES = 80  # seção menor que isso é juntada à seguinte


@dataclass
class TrechoBruto:
    ordem: int
    secao: str
    conteudo: str

    @property
    def tokens_estimados(self) -> int:
        return max(1, len(self.conteudo) // 4)


def _secoes(markdown: str) -> list[tuple[str, str]]:
    """Separa o texto em (caminho de títulos, corpo). Ignora '#' dentro de bloco de código."""
    caminho: list[str] = []
    secoes: list[tuple[str, list[str]]] = [("", [])]
    em_codigo = False

    for linha in markdown.splitlines():
        if CERCA_CODIGO.match(linha):
            em_codigo = not em_codigo
        titulo = None if em_codigo else TITULO.match(linha)
        if titulo:
            nivel = len(titulo.group(1))
            caminho = caminho[: nivel - 1] + [titulo.group(2).strip()]
            secoes.append((" > ".join(caminho), []))
        else:
            secoes[-1][1].append(linha)

    return [(nome, "\n".join(linhas).strip()) for nome, linhas in secoes]


def _paragrafos(corpo: str) -> list[str]:
    """Parágrafos separados por linha em branco; um parágrafo grande demais é partido por linhas."""
    saida: list[str] = []
    for p in (p.strip() for p in re.split(r"\n\s*\n", corpo)):
        if not p:
            continue
        if len(p) <= MAX_CARACTERES:
            saida.append(p)
            continue
        atual: list[str] = []
        for linha in p.splitlines():
            if atual and len("\n".join(atual)) + len(linha) + 1 > MAX_CARACTERES:
                saida.append("\n".join(atual))
                atual = []
            atual.append(linha)
        saida.append("\n".join(atual))
    return saida


def _quebrar(corpo: str) -> list[str]:
    """Quebra um corpo grande em pedaços de até MAX_CARACTERES, repetindo o último parágrafo no pedaço seguinte."""
    if len(corpo) <= MAX_CARACTERES:
        return [corpo]

    pedacos: list[str] = []
    atual: list[str] = []
    tamanho = 0
    for paragrafo in _paragrafos(corpo):
        if atual and tamanho + len(paragrafo) > MAX_CARACTERES:
            pedacos.append("\n\n".join(atual))
            # sobreposição de 1 parágrafo, salvo se ela estouraria o limite junto com o próximo
            atual = [atual[-1]] if len(atual[-1]) + len(paragrafo) <= MAX_CARACTERES else []
            tamanho = sum(len(p) for p in atual)
        atual.append(paragrafo)
        tamanho += len(paragrafo)
    if atual:
        pedacos.append("\n\n".join(atual))
    return pedacos


def dividir_markdown(markdown: str) -> list[TrechoBruto]:
    trechos: list[TrechoBruto] = []
    pendente = ""  # seção curta esperando para entrar na próxima

    for secao, corpo in _secoes(markdown):
        corpo = f"{pendente}\n\n{corpo}".strip() if pendente else corpo
        if len(corpo) < MIN_CARACTERES:
            pendente = corpo
            continue
        pendente = ""
        for pedaco in _quebrar(corpo):
            trechos.append(TrechoBruto(ordem=len(trechos), secao=secao, conteudo=pedaco))

    if pendente and trechos:
        trechos[-1].conteudo += f"\n\n{pendente}"
    return trechos
