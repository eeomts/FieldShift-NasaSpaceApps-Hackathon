"""Usuário (parte 1: login)."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.fazenda import Fazenda


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    nome: Mapped[str] = mapped_column(String(120))
    idioma: Mapped[str] = mapped_column(String(5), default="pt")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    fazenda: Mapped["Fazenda | None"] = relationship(back_populates="usuario", cascade="all, delete-orphan", uselist=False)
