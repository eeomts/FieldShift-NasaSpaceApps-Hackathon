from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app import base
from app.llm.interpretar import Campo, interpretar
from app.models import Usuario
from app.security import usuario_atual

router = APIRouter(tags=["onboarding"])


class Interpretar(BaseModel):
    campo: Campo
    texto: str = Field(max_length=1000)


@router.post("/onboarding/interpretar")
async def interpretar_texto(dados: Interpretar, _: Usuario = Depends(usuario_atual)) -> dict:
    return await run_in_threadpool(interpretar, dados.campo, dados.texto)


@router.get("/culturas")
def listar_culturas(idioma: Literal["pt", "en", "es"] = "pt") -> list[dict]:
    """Base de culturas para a lista reserva (quando a IA não está disponível)."""
    return [
        {"id": c["id"], "nome": base.nome_exibicao(c, idioma), "grupo": c["grupo"], "perene": c["perene"], "tipos": c["tipos"]}
        for c in base.culturas().values()
    ]


@router.get("/equipamentos")
def listar_equipamentos() -> list[dict]:
    return [{"id": e["id"], "nome": e["nome"]} for e in base.equipamentos().values()]
