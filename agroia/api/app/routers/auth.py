from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Usuario
from app.security import confere_senha, cria_token, hash_senha, usuario_atual

router = APIRouter(tags=["auth"])


class Cadastro(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    idioma: Literal["pt", "en", "es"] = "pt"


class Login(BaseModel):
    email: EmailStr
    senha: str = Field(max_length=128)


class UsuarioOut(BaseModel):
    id: str
    nome: str
    email: str
    idioma: str
    onboarding_concluido: bool


class Token(BaseModel):
    token: str
    usuario: UsuarioOut


def _out(u: Usuario) -> UsuarioOut:
    return UsuarioOut(id=str(u.id), nome=u.nome, email=u.email, idioma=u.idioma,
                      onboarding_concluido=bool(u.fazenda and u.fazenda.onboarding_concluido))


@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(dados: Cadastro, db: Session = Depends(get_db)) -> Token:
    u = Usuario(nome=dados.nome.strip(), email=dados.email.lower(), senha_hash=hash_senha(dados.senha), idioma=dados.idioma)
    db.add(u)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma conta com esse e-mail.") from None
    return Token(token=cria_token(u.id), usuario=_out(u))


@router.post("/auth/login", response_model=Token)
def login(dados: Login, db: Session = Depends(get_db)) -> Token:
    u = db.scalar(select(Usuario).where(Usuario.email == dados.email.lower()))
    if not confere_senha(u.senha_hash if u else None, dados.senha) or u is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos.")
    return Token(token=cria_token(u.id), usuario=_out(u))


@router.get("/me", response_model=UsuarioOut)
def me(u: Usuario = Depends(usuario_atual)) -> UsuarioOut:
    return _out(u)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def apagar_conta(u: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)) -> Response:
    """Apaga a conta e todos os dados da fazenda (site-contexto, seção 10)."""
    db.delete(u)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
