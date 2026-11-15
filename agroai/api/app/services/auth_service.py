"""Regras de cadastro, login e conta."""
from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.core.erros import ErroDeNegocio
from app.core.security import confere_senha, cria_token, hash_senha
from app.models import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth import Cadastro, Login, Token, UsuarioOut


def usuario_para_saida(u: Usuario) -> UsuarioOut:
    return UsuarioOut(id=str(u.id), nome=u.nome, email=u.email, idioma=u.idioma,
                      onboarding_concluido=bool(u.fazenda and u.fazenda.onboarding_concluido))


class AuthService:
    def __init__(self, usuarios: UsuarioRepository = Depends()):
        self.usuarios = usuarios

    def cadastrar(self, dados: Cadastro) -> Token:
        u = Usuario(nome=dados.nome.strip(), email=dados.email.lower(), senha_hash=hash_senha(dados.senha), idioma=dados.idioma)
        try:
            self.usuarios.criar(u)
        except IntegrityError:
            raise ErroDeNegocio(409, "Já existe uma conta com esse e-mail.") from None
        return Token(token=cria_token(u.id), usuario=usuario_para_saida(u))

    def entrar(self, dados: Login) -> Token:
        u = self.usuarios.buscar_por_email(dados.email.lower())
        # confere_senha gasta o mesmo tempo quando o e-mail não existe (não revela quais contas existem)
        if not confere_senha(u.senha_hash if u else None, dados.senha) or u is None:
            raise ErroDeNegocio(401, "E-mail ou senha incorretos.")
        return Token(token=cria_token(u.id), usuario=usuario_para_saida(u))

    def atualizar_idioma(self, u: Usuario, idioma: str) -> UsuarioOut:
        return usuario_para_saida(self.usuarios.atualizar_idioma(u, idioma))

    def apagar_conta(self, u: Usuario) -> None:
        self.usuarios.apagar(u)
