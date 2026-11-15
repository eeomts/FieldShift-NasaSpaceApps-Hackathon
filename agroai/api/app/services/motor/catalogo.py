"""Catálogo de culturas do motor: lê data/catalogo/culturas.csv (BR) e eua/culturas.csv (US), com tipos."""
import csv
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal

from app.core.caminhos import RAIZ_REPO

log = logging.getLogger(__name__)

Pais = Literal["BR", "US"]
DIR_CATALOGO = RAIZ_REPO / "data" / "catalogo"
CSV_POR_PAIS: dict[str, Path] = {"BR": DIR_CATALOGO / "culturas.csv", "US": DIR_CATALOGO / "eua" / "culturas.csv"}
CSV_EQUIPAMENTOS = DIR_CATALOGO / "cultura_equipamentos.csv"

CAMPOS_NUMERICOS = (
    "ciclo_dias_min", "ciclo_dias_max", "graus_dia_ciclo_min", "graus_dia_ciclo_max",
    "temp_base_c", "temp_otima_min_c", "temp_otima_max_c", "tmax_critica_c",
    "agua_ciclo_mm_min", "agua_ciclo_mm_max", "kc_inicial", "kc_medio", "kc_final", "profundidade_raiz_m",
    "tmin_critica_c", "fase_frio_inicio_frac", "fase_frio_fim_frac", "tmin_dias_seguidos",
)  # fmt: skip
CAMPOS_BOOLEANOS = ("perene", "sensivel_geada", "fixa_nitrogenio", "raiz_profunda")
CAMPOS_TEXTO = (
    "nome", "nome_cientifico", "familia_botanica", "cobertura_solo", "aporte_biomassa", "valor_forrageiro",
    "confianca_parametros", "codigo_pam", "nome_zarc", "codigo_nass", "calendario_usda",
    "fase_sensivel_frio", "tmin_efeito", "semeadura_inicio", "semeadura_fim", "condicao_semeadura",
)  # fmt: skip


@dataclass(frozen=True)
class CulturaMotor:
    """Uma linha do catálogo. Célula vazia vira None (nunca 0)."""

    id: str
    pais: str
    nome: str
    nome_cientifico: str | None
    familia_botanica: str | None
    tipos: tuple[str, ...]  # comercial, cobertura, forrageira, fixadora_n, raiz_profunda, tolerante_seca
    perene: bool | None
    ciclo_dias_min: float | None
    ciclo_dias_max: float | None
    graus_dia_ciclo_min: float | None
    graus_dia_ciclo_max: float | None
    temp_base_c: float | None
    temp_otima_min_c: float | None
    temp_otima_max_c: float | None
    tmax_critica_c: float | None
    sensivel_geada: bool | None
    agua_ciclo_mm_min: float | None
    agua_ciclo_mm_max: float | None
    kc_inicial: float | None
    kc_medio: float | None
    kc_final: float | None
    profundidade_raiz_m: float | None
    fixa_nitrogenio: bool | None
    raiz_profunda: bool | None
    cobertura_solo: str | None  # baixa | media | alta
    aporte_biomassa: str | None
    valor_forrageiro: str | None  # vazio = "não sei": o critério é ignorado (regra 5)
    confianca_parametros: str | None  # alta | media | baixa
    fontes: tuple[str, ...] = ()
    codigo_pam: str | None = None  # só BR
    nome_zarc: str | None = None  # só BR
    codigo_nass: str | None = None  # só US
    calendario_usda: str | None = None  # só US
    # Frio por fase (regra 17): vazio = None. tmin_efeito: elimina | aviso (None = elimina)
    tmin_critica_c: float | None = None
    fase_sensivel_frio: str | None = None  # floracao | enchimento_grao | ciclo_todo
    fase_frio_inicio_frac: float | None = None  # fração do ciclo médio, contada da semeadura
    fase_frio_fim_frac: float | None = None
    tmin_dias_seguidos: float | None = None  # None = 1 dia
    tmin_efeito: str | None = None
    # Janela de semeadura (regra 12): "MM-DD"; condicao_semeadura = códigos separados por "|"
    semeadura_inicio: str | None = None
    semeadura_fim: str | None = None
    condicao_semeadura: str | None = None
    estados_validos: tuple[str, ...] = ()  # siglas (UF no BR, USPS nos EUA); vazio = sem restrição (regra 13)
    extras: dict[str, str] = field(default_factory=dict, compare=False)  # colunas novas do CSV, sem tipo

    @property
    def dias_seguidos_de_frio(self) -> int:
        """Dias seguidos com Tmin abaixo do limiar para o dano (regra 17): vazio = 1 dia."""
        return max(1, round(self.tmin_dias_seguidos or 1))

    def tem_tipo(self, tipo: str) -> bool:
        return tipo in self.tipos

    def vale_em(self, estado: str | None) -> bool:
        """A base da cultura vale no estado? Sem lista ou sem estado conhecido, não restringe."""
        return not self.estados_validos or estado is None or estado in self.estados_validos


def _texto(v: str | None) -> str | None:
    v = (v or "").strip()
    return v or None


def _numero(v: str | None) -> float | None:
    v = _texto(v)
    return None if v is None else float(v.replace(",", "."))


def _booleano(v: str | None) -> bool | None:
    v = (_texto(v) or "").lower()
    return {"true": True, "false": False}.get(v)


def _lista(v: str | None) -> tuple[str, ...]:
    return tuple(p.strip() for p in (v or "").split("|") if p.strip())


def _linha_para_cultura(linha: dict[str, str], pais: str) -> CulturaMotor:
    conhecidas = {"id", "tipos", "fontes", "estados_validos", *CAMPOS_NUMERICOS, *CAMPOS_BOOLEANOS, *CAMPOS_TEXTO}
    valores = {c: _numero(linha.get(c)) for c in CAMPOS_NUMERICOS}
    valores |= {c: _booleano(linha.get(c)) for c in CAMPOS_BOOLEANOS}
    valores |= {c: _texto(linha.get(c)) for c in CAMPOS_TEXTO}
    return CulturaMotor(
        id=linha["id"].strip(),
        pais=pais,
        tipos=_lista(linha.get("tipos")),
        fontes=_lista(linha.get("fontes")),
        estados_validos=tuple(e.upper() for e in _lista(linha.get("estados_validos"))),
        extras={k: v for k, v in linha.items() if k not in conhecidas and _texto(v)},
        **valores,
    )


def ler_catalogo(caminho: Path, pais: str) -> dict[str, CulturaMotor]:
    with caminho.open(encoding="utf-8", newline="") as f:
        return {c.id: c for c in (_linha_para_cultura(l, pais) for l in csv.DictReader(f))}


@lru_cache
def catalogo_do_pais(pais: Pais) -> dict[str, CulturaMotor]:
    """Culturas candidatas do país, por id. EUA sem CSV (ainda em construção): dicionário vazio e aviso."""
    caminho = CSV_POR_PAIS.get(pais)
    if caminho is None:
        raise ValueError(f"País sem catálogo: {pais!r}")
    if not caminho.exists():
        log.warning("Catálogo do motor sem arquivo para %s (%s): nenhuma cultura candidata.", pais, caminho.name)
        return {}
    return ler_catalogo(caminho, pais)


@lru_cache
def equipamentos_por_cultura() -> dict[str, dict[str, set[str]]]:
    """{cultura_id: {etapa ('plantio'|'colheita'): {equipamento_id}}}: equipamentos que servem a cultura em cada etapa."""
    saida: dict[str, dict[str, set[str]]] = {}
    with CSV_EQUIPAMENTOS.open(encoding="utf-8", newline="") as f:
        for l in csv.DictReader(f):
            saida.setdefault(l["cultura_id"].strip(), {}).setdefault(l["etapa"].strip(), set()).add(l["equipamento_id"].strip())
    return saida
