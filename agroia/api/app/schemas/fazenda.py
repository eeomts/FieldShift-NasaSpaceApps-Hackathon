"""Entrada e saída das rotas da fazenda (≈ FormRequest + Resource)."""
from pydantic import BaseModel, Field

from app.schemas.onboarding import Respostas


class SalvarFazenda(BaseModel):
    respostas: Respostas
    passo_atual: int = Field(default=0, ge=0, le=50)
    concluir: bool = False


class FazendaOut(BaseModel):
    id: str
    respostas: Respostas
    passo_atual: int
    onboarding_concluido: bool
    status_processamento: str
    perfil: str | None
    papel: str | None
    modificadores: dict
    retrato_solo: dict
    proximos_passos: list[dict]
    meses_sem_cobertura: list[int]
