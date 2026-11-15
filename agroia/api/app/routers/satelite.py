"""Rota do satélite da fazenda (Dashboard)."""
from dataclasses import asdict

from fastapi import APIRouter, Depends

from app.core.erros import ErroDeNegocio
from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.satelite import Satelite
from app.services.satelite.satelite_service import SateliteService

router = APIRouter(tags=["satelite"])


@router.get("/fazenda/satelite", response_model=Satelite)
def satelite(u: Usuario = Depends(usuario_atual), servico: SateliteService = Depends()) -> Satelite:
    """Umidade do solo (SMAP), NDVI (MODIS) e chuva dos últimos 30 dias (IMERG ou NASA POWER) no ponto da fazenda."""
    f = u.fazenda
    if f is None:
        raise ErroDeNegocio(404, "Fazenda ainda não cadastrada.")
    if f.lat is None or f.lon is None:
        raise ErroDeNegocio(422, "Marque no mapa onde fica o campo para ver os dados de satélite.")
    return Satelite(**asdict(servico.obter(f.lat, f.lon)))
