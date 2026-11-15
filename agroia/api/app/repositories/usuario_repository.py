"""Acesso ao banco para usuários."""
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Usuario


class UsuarioRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def criar(self, usuario: Usuario) -> Usuario:
        """Grava o usuário. Lança IntegrityError (já desfeito) se o e-mail já existe."""
        self.db.add(usuario)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        return usuario

    def atualizar_idioma(self, usuario: Usuario, idioma: str) -> Usuario:
        usuario.idioma = idioma
        self.db.commit()
        return usuario

    def apagar(self, usuario: Usuario) -> None:
        """Apaga o usuário e, em cascata, a fazenda e tudo ligado a ela."""
        self.db.delete(usuario)
        self.db.commit()
