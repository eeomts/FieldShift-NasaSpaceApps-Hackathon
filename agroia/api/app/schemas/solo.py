"""Formato do solo no retrato da fazenda (contrato do PLANO-SOLO-V1)."""
from typing import Literal

from pydantic import BaseModel, Field

FonteSolo = Literal["laudo", "teste_campo", "produtor", "soilgrids"]
Atributo = Literal["textura", "materia_organica", "acidez"]
Confianca = Literal["alta", "media", "baixa"]


class EvidenciaSolo(BaseModel):
    fonte: FonteSolo
    valor: str
    peso: float
    texto: str


class AtributoSolo(BaseModel):
    atributo: Atributo
    valor: str | None = None
    confianca: Confianca | None = None
    evidencias: list[EvidenciaSolo] = Field(default_factory=list)
    divergencia: str | None = None


class SoloPonto(BaseModel):
    """Solo de 0 a 30 cm no ponto (SoilGrids). Ausente = None, nunca 0."""

    argila_pct: float | None = None
    areia_pct: float | None = None
    silte_pct: float | None = None
    carbono_g_kg: float | None = None
    materia_organica_g_kg: float | None = None
    ph: float | None = None
    ctc_cmol_kg: float | None = None
    densidade_g_cm3: float | None = None
    classe_textural: str | None = None
    k_usle: float | None = None  # t·ha·h/(ha·MJ·mm)
    incerteza: dict[str, float | None] = Field(default_factory=dict)  # (Q0,95 − Q0,05) ÷ Q0,50, por campo acima
    camada: Literal["0–30 cm"] = "0–30 cm"
    fonte: str = "SoilGrids 2.0 (ISRIC), 250 m"
    sem_dado: bool = False  # área urbana ou água
