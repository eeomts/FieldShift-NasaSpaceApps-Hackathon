"""Entrada e saída das rotas da fazenda."""
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.onboarding import Respostas
from app.schemas.solo import AtributoSolo, SoloPonto

StatusProcessamento = Literal["pendente", "processando", "pronto", "erro"]


class SalvarFazenda(BaseModel):
    respostas: Respostas
    passo_atual: int = Field(default=0, ge=0, le=50)
    concluir: bool = False


class RetratoSolo(BaseModel):
    """`indicadores` e `figuras` vêm das respostas; `sintese` e `soilgrids` (acréscimos) da fusão com o mapa global."""

    fonte: str = "produtor"
    indicadores: list[dict] = Field(default_factory=list)
    figuras: dict | None = None
    sintese: list[AtributoSolo] = Field(default_factory=list)
    soilgrids: SoloPonto | None = None


class FazendaOut(BaseModel):
    id: str
    respostas: Respostas
    passo_atual: int
    onboarding_concluido: bool
    status_processamento: StatusProcessamento
    perfil: str | None
    papel: str | None
    modificadores: dict
    retrato_solo: RetratoSolo
    proximos_passos: list[dict]
    meses_sem_cobertura: list[int]
