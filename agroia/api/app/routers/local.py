"""Rotas de local: busca de lugar pelo nome e informações de um ponto (exigem login)."""
from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.local import InfoLocal, LugarBusca
from app.services.local.local_service import LocalService

router = APIRouter(prefix="/local", tags=["local"])


@router.get("/buscar", response_model=list[LugarBusca])
def buscar(
    q: str = Query(min_length=2, max_length=120),
    idioma: Literal["pt", "en"] = "pt",
    _: Usuario = Depends(usuario_atual),
    servico: LocalService = Depends(),
) -> list[LugarBusca]:
    return servico.buscar(q, idioma)


@router.get("/info", response_model=InfoLocal)
def info(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    idioma: Literal["pt", "en"] = "pt",
    _: Usuario = Depends(usuario_atual),
    servico: LocalService = Depends(),
) -> InfoLocal:
    return servico.info(lat, lon, idioma)
