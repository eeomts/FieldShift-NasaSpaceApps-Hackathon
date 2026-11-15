"""Cria a API, liga as rotas e trata os erros de negócio."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.erros import ErroDeNegocio
from app.routers import auth, chat, fazenda, onboarding

app = FastAPI(title="AgroIA API", version="0.1.0")


@app.exception_handler(ErroDeNegocio)
def erro_de_negocio(_: Request, erro: ErroDeNegocio) -> JSONResponse:
    """Mesmo formato do HTTPException: {"detail": "<mensagem>"}."""
    return JSONResponse(status_code=erro.status_code, content={"detail": erro.mensagem})

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_list,
    allow_origin_regex=get_settings().cors_origin_regex,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(fazenda.router)
app.include_router(onboarding.router)
app.include_router(chat.router)


@app.get("/saude")
def saude() -> dict:
    return {"ok": True}
