"""Conversas do chat (com o conteúdo completo do Gemini) e o registro das buscas no RAG."""
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Conversa(Base):
    __tablename__ = "conversa"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"), index=True)
    titulo: Mapped[str | None] = mapped_column(String(80))  # início da primeira pergunta
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mensagens: Mapped[list["Mensagem"]] = relationship(
        order_by="Mensagem.id", cascade="all, delete-orphan", passive_deletes=True
    )


class Mensagem(Base):
    """Um turno do Gemini. `conteudo` guarda o Content completo (chamadas de ferramenta e assinaturas), que volta no histórico."""

    __tablename__ = "mensagem"
    __table_args__ = (CheckConstraint("papel IN ('user','model')", name="ck_mensagem_papel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    conversa_id: Mapped[int] = mapped_column(ForeignKey("conversa.id", ondelete="CASCADE"), index=True)
    papel: Mapped[str] = mapped_column(String(10))  # papel do Gemini: user | model
    conteudo: Mapped[Any] = mapped_column(JSONB)
    visivel: Mapped[bool] = mapped_column(Boolean, default=False)  # só a pergunta do produtor e a resposta final
    texto: Mapped[str | None] = mapped_column(Text)
    fontes: Mapped[list] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"))
    ferramentas_usadas: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list, server_default=text("'{}'"))
    tokens_entrada: Mapped[int | None] = mapped_column(Integer)
    tokens_saida: Mapped[int | None] = mapped_column(Integer)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BuscaLog(Base):
    """Cada busca no RAG: as palavras do produtor e a consulta reescrita (auditoria e expressões regionais)."""

    __tablename__ = "busca_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversa_id: Mapped[int | None] = mapped_column(ForeignKey("conversa.id", ondelete="SET NULL"), index=True)
    expressao_original: Mapped[str | None] = mapped_column(Text)
    consulta: Mapped[str] = mapped_column(Text)
    filtros: Mapped[Any | None] = mapped_column(JSONB)
    trechos_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list, server_default=text("'{}'"))
    notas: Mapped[list[float]] = mapped_column(ARRAY(Float), default=list, server_default=text("'{}'"))
    descartados: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # abaixo da similaridade mínima
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
