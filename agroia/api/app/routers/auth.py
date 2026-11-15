"""Rotas de cadastro, login e conta."""
from fastapi import APIRouter, Depends, Response, status

from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.auth import Cadastro, Login, Token, UsuarioOut
from app.services.auth_service import AuthService, usuario_para_saida

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(dados: Cadastro, servico: AuthService = Depends()) -> Token:
    return servico.cadastrar(dados)


@router.post("/auth/login", response_model=Token)
def login(dados: Login, servico: AuthService = Depends()) -> Token:
    return servico.entrar(dados)


@router.get("/me", response_model=UsuarioOut)
def me(u: Usuario = Depends(usuario_atual)) -> UsuarioOut:
    return usuario_para_saida(u)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def apagar_conta(u: Usuario = Depends(usuario_atual), servico: AuthService = Depends()) -> Response:
    """Apaga a conta e todos os dados da fazenda (site-contexto, seção 10)."""
    servico.apagar_conta(u)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
