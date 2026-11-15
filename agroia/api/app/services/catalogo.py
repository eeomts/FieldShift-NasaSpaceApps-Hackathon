"""Carrega a base de culturas e equipamentos (agroia/base/*.json) e faz o casamento por sinônimos."""
import json
import re
import unicodedata
from functools import lru_cache

from app.core.caminhos import RAIZ_REPO

BASE_DIR = RAIZ_REPO / "agroia" / "base"


def normaliza(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", sem_acento.lower()).strip()


@lru_cache
def culturas() -> dict[str, dict]:
    dados = json.loads((BASE_DIR / "culturas.json").read_text(encoding="utf-8"))
    return {c["id"]: c for c in dados["culturas"]}


@lru_cache
def equipamentos() -> dict[str, dict]:
    dados = json.loads((BASE_DIR / "equipamentos.json").read_text(encoding="utf-8"))
    return {e["id"]: e for e in dados["equipamentos"]}


def nome_exibicao(item: dict, idioma: str = "pt") -> str:
    if "nome" in item:
        return item["nome"]
    nomes = item["nomes"].get(idioma) or item["nomes"]["pt"]
    return nomes[0][:1].upper() + nomes[0][1:]


def _indice(itens: dict[str, dict]) -> list[tuple[str, str]]:
    """(sinônimo normalizado, id), do mais longo para o mais curto."""
    pares = {(normaliza(n), item_id) for item_id, item in itens.items() for ns in item["nomes"].values() for n in ns}
    return sorted(pares, key=lambda p: -len(p[0]))


def casa_texto(texto: str, itens: dict[str, dict]) -> list[dict]:
    """Casamento simples por sinônimos. É a reserva quando a IA não está disponível.

    Devolve [{id, texto_original}] na ordem em que aparecem no texto, sem repetir.
    """
    alvo = f" {normaliza(texto)} "
    achados: list[tuple[int, str, str]] = []
    ocupado: list[tuple[int, int]] = []
    for sinonimo, item_id in _indice(itens):
        for m in re.finditer(rf"(?<= ){re.escape(sinonimo)}(?= )", alvo):
            ini, fim = m.start(), m.end()
            if any(ini < f and fim > i for i, f in ocupado):
                continue
            ocupado.append((ini, fim))
            achados.append((ini, item_id, sinonimo))
    vistos: set[str] = set()
    saida = []
    for _, item_id, sinonimo in sorted(achados):
        if item_id not in vistos:
            vistos.add(item_id)
            saida.append({"id": item_id, "texto_original": sinonimo})
    return saida


def listar_culturas(idioma: str = "pt") -> list[dict]:
    """Culturas para a lista reserva do onboarding (quando a IA não está disponível)."""
    return [
        {"id": c["id"], "nome": nome_exibicao(c, idioma), "grupo": c["grupo"], "perene": c["perene"], "tipos": c["tipos"]}
        for c in culturas().values()
    ]


def listar_equipamentos(idioma: str = "pt") -> list[dict]:
    """Equipamentos com o nome no idioma (en usa `nome_en`; sem tradução, cai no português)."""
    campo = "nome_en" if idioma == "en" else "nome"
    return [{"id": e["id"], "nome": e.get(campo) or e["nome"]} for e in equipamentos().values()]
