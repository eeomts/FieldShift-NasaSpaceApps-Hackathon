"""Rotas da fazenda (questionário)."""
from fastapi import APIRouter, Depends

from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.fazenda import FazendaOut, SalvarFazenda
from app.services.onboarding.fazenda_service import FazendaService

router = APIRouter(tags=["fazenda"])


@router.get("/fazenda", response_model=FazendaOut)
def ler(u: Usuario = Depends(usuario_atual), servico: FazendaService = Depends()) -> FazendaOut:
    return servico.ler(u)


@router.put("/fazenda", response_model=FazendaOut)
def salvar(dados: SalvarFazenda, u: Usuario = Depends(usuario_atual), servico: FazendaService = Depends()) -> FazendaOut:
    """Salva o questionário (parcial ou completo). Com concluir=true, exige o local do campo."""
    return servico.salvar(u, dados)
