"""Rota da comparação de rotações da fazenda."""
from fastapi import APIRouter, Depends

from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.estrategias import Analise
from app.services.motor.estrategias_service import EstrategiasService

router = APIRouter(tags=["estrategias"])


@router.get("/fazenda/estrategias", response_model=Analise)
def comparar(u: Usuario = Depends(usuario_atual), servico: EstrategiasService = Depends()) -> Analise:
    """Compara a rotação atual com alternativas, na hora (a 1ª vez numa região baixa o NASA POWER)."""
    return servico.comparar(u)
