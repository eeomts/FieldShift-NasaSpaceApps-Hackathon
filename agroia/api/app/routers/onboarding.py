"""Rotas de apoio ao onboarding (≈ Controller): texto livre com IA e listas do catálogo."""
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.onboarding import Interpretar
from app.services import catalogo
from app.services.interpretacao import interpretar

router = APIRouter(tags=["onboarding"])


@router.post("/onboarding/interpretar")
async def interpretar_texto(dados: Interpretar, _: Usuario = Depends(usuario_atual)) -> dict:
    return await run_in_threadpool(interpretar, dados.campo, dados.texto)


@router.get("/culturas")
def listar_culturas(idioma: Literal["pt", "en", "es"] = "pt") -> list[dict]:
    """Base de culturas para a lista reserva (quando a IA não está disponível)."""
    return catalogo.listar_culturas(idioma)


@router.get("/equipamentos")
def listar_equipamentos() -> list[dict]:
    return catalogo.listar_equipamentos()
