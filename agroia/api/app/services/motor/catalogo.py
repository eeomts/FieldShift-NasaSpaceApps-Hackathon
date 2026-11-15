"""Catálogo de culturas do motor: lê culturas.csv (BR e US) com tipos e o bloco regua das evidências."""
import csv
import json
import logging
from dataclasses import dataclass, field, replace
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from app.core.caminhos import RAIZ_REPO
from app.services.motor.parametros import ARRANJOS_DE_CONSORCIO, PALHADA_ALTA_T_HA, PALHADA_MEDIA_T_HA

log = logging.getLogger(__name__)

Pais = Literal["BR", "US"]
DIR_CATALOGO = RAIZ_REPO / "data" / "catalogo"
CSV_POR_PAIS: dict[str, Path] = {"BR": DIR_CATALOGO / "culturas.csv", "US": DIR_CATALOGO / "eua" / "culturas.csv"}
CSV_EQUIPAMENTOS = DIR_CATALOGO / "cultura_equipamentos.csv"

CAMPOS_NUMERICOS = (
    "ciclo_dias_min", "ciclo_dias_max", "graus_dia_ciclo_min", "graus_dia_ciclo_max",
    "temp_base_c", "temp_otima_min_c", "temp_otima_max_c", "tmax_critica_c",
    "agua_ciclo_mm_min", "agua_ciclo_mm_max", "kc_inicial", "kc_medio", "kc_final", "profundidade_raiz_m",
)  # fmt: skip
CAMPOS_BOOLEANOS = ("perene", "sensivel_geada", "fixa_nitrogenio", "raiz_profunda")
CAMPOS_TEXTO = (
    "nome", "nome_cientifico", "familia_botanica", "cobertura_solo", "aporte_biomassa", "valor_forrageiro",
    "confianca_parametros", "codigo_pam", "nome_zarc", "codigo_nass", "calendario_usda",
    "tipo_manejo", "lacuna_informacao", "risco_revisao_local",
)  # fmt: skip
CAMPOS_MES_DIA = ("semeadura_inicio", "semeadura_fim", "manejo_inicio", "manejo_fim")  # "MM-DD" no CSV
CAMPOS_LISTA = ("tipos", "fontes", "estados_validos", "condicao_semeadura")  # separados por |

MesDia = tuple[int, int]  # (mês, dia)


@dataclass(frozen=True)
class FaixaPalhada:
    """Massa seca de palhada em t/ha (regua.ms_palhada_t_ha); ausente = None."""

    minimo: float | None = None
    tipico: float | None = None
    maximo: float | None = None


@dataclass(frozen=True)
class ArranjoRegional:
    """Um arranjo de regua.arranjos. Os campos seguem os nomes das colunas do CSV; ausente = None."""

    nome: str
    estados: tuple[str, ...] = ()  # vazio = o arquivo não traz lista
    regional: bool = True  # False: consórcio (regra 4) ou outro sistema na mesma região; a regra 13 (região) não usa
    ciclo_dias_min: float | None = None
    ciclo_dias_max: float | None = None
    graus_dia_ciclo_min: float | None = None
    graus_dia_ciclo_max: float | None = None
    agua_ciclo_mm_min: float | None = None
    agua_ciclo_mm_max: float | None = None
    semeadura_inicio: MesDia | None = None
    semeadura_fim: MesDia | None = None
    manejo_inicio: MesDia | None = None
    manejo_fim: MesDia | None = None
    tipo_manejo: str | None = None
    condicao_semeadura: tuple[str, ...] = ()
    palhada: FaixaPalhada | None = None
    origem: dict[str, str] = field(default_factory=dict, compare=False)  # tipo de origem de cada número


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
    estados_validos: tuple[str, ...] = ()  # siglas (UF no BR, USPS nos EUA); vazio = sem restrição (regra 13)
    semeadura_inicio: MesDia | None = None  # janela de semeadura na região de referência (regra 12)
    semeadura_fim: MesDia | None = None
    manejo_inicio: MesDia | None = None
    manejo_fim: MesDia | None = None
    tipo_manejo: str | None = None  # dessecacao | morte_pelo_frio | rolagem | corte
    condicao_semeadura: tuple[str, ...] = ()  # depois de quê a cobertura pode ser semeada
    lacuna_informacao: str | None = None  # texto para o produtor (regra 10)
    risco_revisao_local: str | None = None
    avisos: dict[str, str] = field(default_factory=dict, compare=False)  # regua.avisos: coluna -> texto (regra 16)
    depende_da_epoca: dict[str, bool | None] = field(default_factory=dict, compare=False)  # coluna -> bool (regra 15)
    faixa_palhada: FaixaPalhada | None = None  # regua.ms_palhada_t_ha
    arranjos: tuple[ArranjoRegional, ...] = ()  # regua.arranjos
    arranjo_aplicado: str | None = None  # nome do arranjo regional cujos números substituíram os da linha (regra 13)
    extras: dict[str, str] = field(default_factory=dict, compare=False)  # colunas novas do CSV, sem tipo

    def tem_tipo(self, tipo: str) -> bool:
        return tipo in self.tipos

    @property
    def e_cobertura(self) -> bool:
        """Planta de cobertura: tem o tipo cobertura e não é comercial."""
        return "cobertura" in self.tipos and "comercial" not in self.tipos

    @property
    def arranjos_regionais(self) -> tuple[ArranjoRegional, ...]:
        return tuple(a for a in self.arranjos if a.regional)

    def vale_em(self, estado: str | None) -> bool:
        """A base da cultura vale no estado? Sem lista ou sem estado conhecido, não restringe."""
        return not self.estados_validos or estado is None or estado in self.estados_validos


@dataclass(frozen=True)
class JanelaSemeadura:
    inicio: MesDia
    fim: MesDia
    condicao_semeadura: tuple[str, ...] = ()  # vazio = sem restrição pela cultura anterior


def janela_de_semeadura(c: CulturaMotor, estado: str | None = None) -> JanelaSemeadura | None:
    """Janela de semeadura da cobertura (regra 12); None = não confirmada. Único ponto de leitura (regra 13 troca pelo arranjo)."""
    if c.semeadura_inicio is None or c.semeadura_fim is None:
        return None
    return JanelaSemeadura(c.semeadura_inicio, c.semeadura_fim, c.condicao_semeadura)


def classe_da_palhada(t_ha: float) -> str:
    """Régua do README do catálogo: baixo < 2,3; médio de 2,3 a < 6; alto a partir de 6 t/ha de matéria seca."""
    return "baixo" if t_ha < PALHADA_MEDIA_T_HA else "medio" if t_ha < PALHADA_ALTA_T_HA else "alto"


# Campos que o arranjo regional substitui quando traz valor (None no arranjo = mantém o da linha)
CAMPOS_DO_ARRANJO = (
    "ciclo_dias_min", "ciclo_dias_max", "graus_dia_ciclo_min", "graus_dia_ciclo_max", "agua_ciclo_mm_min", "agua_ciclo_mm_max",
    "semeadura_inicio", "semeadura_fim", "manejo_inicio", "manejo_fim", "tipo_manejo",
)  # fmt: skip


def cultura_no_estado(c: CulturaMotor, estado: str | None) -> CulturaMotor:
    """Regra 13: se o estado está num arranjo regional da cultura, os números do arranjo valem no lugar dos da linha.

    A cultura passa a valer no estado do arranjo mesmo fora de `estados_validos`. Sem estado ou sem arranjo: a própria `c`.
    """
    if estado is None:
        return c
    achados = [a for a in c.arranjos_regionais if estado in a.estados]
    if not achados:
        return c
    if len(achados) > 1:
        log.warning("Cultura %s tem %d arranjos regionais para %s; usando %s.", c.id, len(achados), estado, achados[0].nome)
    a = achados[0]
    mudancas: dict[str, Any] = {k: v for k in CAMPOS_DO_ARRANJO if (v := getattr(a, k)) is not None}
    if a.condicao_semeadura:
        mudancas["condicao_semeadura"] = a.condicao_semeadura
    if a.palhada is not None:
        mudancas["faixa_palhada"] = a.palhada
        if a.palhada.minimo is not None and a.palhada.maximo is not None:  # regra 15: depende da época se min e max caem em classes diferentes
            mudancas["depende_da_epoca"] = {**c.depende_da_epoca, "aporte_biomassa": classe_da_palhada(a.palhada.minimo) != classe_da_palhada(a.palhada.maximo)}
        if a.palhada.tipico is not None:  # sem típico, a classe da linha fica
            mudancas["aporte_biomassa"] = classe_da_palhada(a.palhada.tipico)
    if c.estados_validos and estado not in c.estados_validos:
        mudancas["estados_validos"] = c.estados_validos + (estado,)
    return replace(c, arranjo_aplicado=a.nome, **mudancas)


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


def _mes_dia(v: str | None, contexto: str) -> MesDia | None:
    """'MM-DD' vira (mês, dia); vazio = None; formato ou data inválida = erro claro."""
    v = _texto(v)
    if v is None:
        return None
    try:
        if len(v) != 5 or v[2] != "-":
            raise ValueError
        mes, dia = int(v[:2]), int(v[3:])
        date(2000, mes, dia)  # 2000 é bissexto: aceita 02-29
    except ValueError:
        raise ValueError(f"{contexto}: data {v!r} inválida, esperado MM-DD") from None
    return mes, dia


def _faixa(d: Any) -> FaixaPalhada | None:
    if not isinstance(d, dict):
        return None
    f = FaixaPalhada(d.get("min"), d.get("tipico"), d.get("max"))
    return None if f == FaixaPalhada() else f


def _arranjo(nome: str, a: dict[str, Any], contexto: str) -> ArranjoRegional:
    valores: dict[str, Any] = {}
    for chave in ("ciclo_dias", "graus_dia_ciclo", "agua_ciclo_mm"):
        faixa = a.get(chave) if isinstance(a.get(chave), dict) else {}
        valores |= {f"{chave}_min": faixa.get("min"), f"{chave}_max": faixa.get("max")}
    valores |= {c: _mes_dia(a.get(c), f"{contexto}, arranjo {nome}, {c}") for c in CAMPOS_MES_DIA}
    return ArranjoRegional(
        nome=nome,
        estados=tuple(e.upper() for e in _lista(a.get("estados"))),
        regional=nome not in ARRANJOS_DE_CONSORCIO and not _texto(a.get("sistema")),  # "sistema": outro manejo nos mesmos estados da linha
        tipo_manejo=_texto(a.get("tipo_manejo")),
        condicao_semeadura=_lista(a.get("condicao_semeadura")),
        palhada=_faixa(a.get("ms_palhada_t_ha")),
        origem={k: v for k, v in (a.get("origem") or {}).items() if isinstance(v, str)},
        **valores,
    )


def _regua(caminho_csv: Path, cultura_id: str) -> dict[str, Any]:
    """Bloco regua do arquivo de evidência da cultura; arquivo ausente ou sem o bloco = {}."""
    arquivo = caminho_csv.parent / "evidencias" / f"{cultura_id}.json"
    if not arquivo.exists():
        return {}
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Evidência {arquivo.name} com JSON inválido: {e}") from e
    regua = dados.get("regua") if isinstance(dados, dict) else None
    return regua if isinstance(regua, dict) else {}


def _campos_da_regua(regua: dict[str, Any], contexto: str) -> dict[str, Any]:
    avisos = {k: v.strip() for k, v in (regua.get("avisos") or {}).items() if isinstance(v, str) and v.strip()}
    dep = (regua.get("detalhe") or {}).get("depende_da_epoca") or {}
    return {
        "avisos": avisos,
        "depende_da_epoca": {k: v for k, v in dep.items() if v is None or isinstance(v, bool)},
        "faixa_palhada": _faixa(regua.get("ms_palhada_t_ha")),
        "arranjos": tuple(_arranjo(n, a, contexto) for n, a in (regua.get("arranjos") or {}).items() if isinstance(a, dict)),
    }


def _linha_para_cultura(linha: dict[str, str], pais: str, regua: dict[str, Any] | None = None) -> CulturaMotor:
    conhecidas = {"id", *CAMPOS_LISTA, *CAMPOS_MES_DIA, *CAMPOS_NUMERICOS, *CAMPOS_BOOLEANOS, *CAMPOS_TEXTO}
    id_ = linha["id"].strip()
    contexto = f"Cultura {id_} ({pais})"
    valores = {c: _numero(linha.get(c)) for c in CAMPOS_NUMERICOS}
    valores |= {c: _booleano(linha.get(c)) for c in CAMPOS_BOOLEANOS}
    valores |= {c: _texto(linha.get(c)) for c in CAMPOS_TEXTO}
    valores |= {c: _mes_dia(linha.get(c), f"{contexto}, {c}") for c in CAMPOS_MES_DIA}
    return CulturaMotor(
        id=id_,
        pais=pais,
        tipos=_lista(linha.get("tipos")),
        fontes=_lista(linha.get("fontes")),
        estados_validos=tuple(e.upper() for e in _lista(linha.get("estados_validos"))),
        condicao_semeadura=_lista(linha.get("condicao_semeadura")),
        extras={k: v for k, v in linha.items() if k not in conhecidas and _texto(v)},
        **_campos_da_regua(regua or {}, contexto),
        **valores,
    )


def ler_catalogo(caminho: Path, pais: str) -> dict[str, CulturaMotor]:
    """Lê o CSV; a régua vem de evidencias/<id>.json ao lado dele (ausente = campos vazios)."""
    with caminho.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    return {c.id: c for c in (_linha_para_cultura(l, pais, _regua(caminho, l["id"].strip())) for l in linhas)}


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
