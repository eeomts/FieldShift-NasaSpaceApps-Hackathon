"""Lista reserva do texto livre (sem Gemini ou quando ele falha): nomes da base, meses, estações, consórcio e motivo.

Trabalha frase a frase. As culturas de uma mesma frase compartilham os meses citados nela.
Devolve dicts com as chaves de `_ItemIA` (interpretacao.py); a validação final é a mesma da IA.
"""
import re

from app.services import catalogo
from app.services.catalogo import normaliza

_FRASES = re.compile(r"[.;!?\n]+")

# Meses por nome, no idioma do produtor ("out" e "mai" só em pt; "may" só em en).
_MESES = {
    "pt": ["janeiro|jan", "fevereiro|fev", "marco|mar", "abril|abr", "maio|mai", "junho|jun",
           "julho|jul", "agosto|ago", "setembro|set", "outubro|out", "novembro|nov", "dezembro|dez"],
    "en": ["january|jan", "february|feb", "march|mar", "april|apr", "may", "june|jun",
           "july|jul", "august|aug", "september|sept|sep", "october|oct", "november|nov", "december|dec"],
}
# "dez" também é o número dez: só vale como mês depois de uma destas palavras.
_ANTES_DE_DEZ = {"de", "em", "ate", "a", "ao", "ou", "e", "desde", "para", "entre"}

# Estações -> mês de início (Sul, Norte).
_INICIO = {"verao": (12, 6), "outono": (3, 9), "inverno": (6, 12), "primavera": (9, 3),
           "chuvas": (10, 6), "seca": (5, 11)}
_ESTACOES = {
    "pt": {"verao": "verao", "outono": "outono", "inverno": "inverno", "primavera": "primavera"},
    "en": {"verao": "summer", "outono": "autumn|fall", "inverno": "winter", "primavera": "spring"},
}
_ESTACOES_COMUNS = {"chuvas": "chuvas|chuvosa|chuvoso|aguas|rainy|wet season", "seca": "seca|estiagem|dry season"}

_PARADO = re.compile(r"\b(parado|parada|vazio|vazia|idle|fallow)\b")
_JUNTO = re.compile(r"\b(junto|juntos|juntas|consorci\w*|together|intercrop\w*)\b")
_ANO_TODO = re.compile(r"\b(ano todo|all year|year round)\b")
_MOTIVOS = [
    ("mercado", re.compile(r"\b(mercado|vender|venda|preco|market|sell|selling)\b")),
    ("costume", re.compile(r"\b(costume|tradicao|custom|tradition)\b")),
    ("deu_errado", re.compile(r"\b(deu errado|perdi|praga|failed|went wrong)\b")),
]


def _ordem(texto: str, padroes: dict[str, str]) -> list[tuple[int, str]]:
    """[(posição, chave)] de cada padrão achado no texto normalizado, em ordem."""
    achados = []
    for chave, alternativas in padroes.items():
        for m in re.finditer(rf"\b({alternativas})\b", texto):
            achados.append((m.start(), chave))
    return sorted(achados)


def _meses_citados(frase: str, idioma: str) -> list[int]:
    nomes = {str(i + 1): alt for i, alt in enumerate(_MESES.get(idioma, _MESES["pt"]))}
    meses = []
    for pos, chave in _ordem(frase, nomes):
        if chave == "12" and idioma == "pt":
            antes = frase[:pos].split()
            if not antes or antes[-1] not in _ANTES_DE_DEZ:
                continue
        meses.append(int(chave))
    return meses


def _estacoes_citadas(frase: str, idioma: str) -> list[str]:
    padroes = _ESTACOES.get(idioma, _ESTACOES["pt"]) | _ESTACOES_COMUNS
    vistas: list[str] = []
    for _, chave in _ordem(frase, padroes):
        if chave not in vistas:
            vistas.append(chave)
    return vistas


def _soma_meses(mes: int, n: int) -> int:
    return (mes - 1 + n) % 12 + 1


def _epoca(frase: str, hemisferio: str, idioma: str) -> tuple[int | None, int | None]:
    """(início, fim) pelos meses citados; sem meses, pelas estações; senão (None, None)."""
    meses = _meses_citados(frase, idioma)
    if meses:
        return meses[0], (meses[1] if len(meses) > 1 else None)
    estacoes = _estacoes_citadas(frase, idioma)
    if not estacoes:
        return None, None
    lado = 0 if hemisferio == "S" else 1
    ini = _INICIO[estacoes[0]][lado]
    if len(estacoes) == 1:
        return ini, _soma_meses(ini, 3)
    segunda = _INICIO[estacoes[1]][lado]
    fim = _soma_meses(segunda, -1) if _PARADO.search(frase) else segunda
    return ini, fim


def _culturas_da_frase(frase: str) -> list[dict]:
    return catalogo.casa_texto(frase, catalogo.culturas())


def _itens_culturas(frases: list[str], hemisferio: str, idioma: str) -> list[dict]:
    itens: list[dict] = []
    for frase in frases:
        achadas = _culturas_da_frase(frase)
        if not achadas:
            continue
        ini, fim = _epoca(frase, hemisferio, idioma)
        junto = len(achadas) >= 2 and bool(_JUNTO.search(frase))
        perene = len(achadas) == 1 and bool(_ANO_TODO.search(frase))
        for a in achadas:
            novo = {"texto_original": a["texto_original"], "id": a["id"], "inicio_mes": ini, "fim_mes": fim,
                    "perene": perene or None,
                    "consorcio_com": [b["id"] for b in achadas if b["id"] != a["id"]] if junto else []}
            existente = next((i for i in itens if i["id"] == a["id"]), None)
            if existente is None:
                itens.append(novo)
            elif existente["inicio_mes"] is None and ini is not None:
                existente.update(inicio_mes=ini, fim_mes=fim, perene=novo["perene"])
                existente["consorcio_com"] = sorted(set(existente["consorcio_com"]) | set(novo["consorcio_com"]))
            elif ini is not None and (ini, fim) != (existente["inicio_mes"], existente["fim_mes"]):
                itens.append(novo)  # a mesma cultura em outra época vira outro item
    return itens


def _itens_excluidas(frases: list[str]) -> list[dict]:
    itens: dict[str, dict] = {}
    for frase in frases:
        motivo = next((m for m, rx in _MOTIVOS if rx.search(frase)), None)
        for a in _culturas_da_frase(frase):
            itens.setdefault(a["id"], {"texto_original": a["texto_original"], "id": a["id"], "motivo": motivo})
    return list(itens.values())


def itens_da_reserva(campo: str, texto: str, hemisferio: str = "S", idioma: str = "pt") -> list[dict]:
    """Casa o texto com a base, sem IA."""
    if campo == "equipamentos":
        return [{"texto_original": a["texto_original"], "id": a["id"]}
                for a in catalogo.casa_texto(texto, catalogo.equipamentos())]
    frases = [f for f in (normaliza(p) for p in _FRASES.split(texto)) if f]
    if campo == "culturas":
        return _itens_culturas(frases, hemisferio, idioma)
    return _itens_excluidas(frases)
