"""Base de conhecimento do RAG: documentos e trechos com embedding e busca textual."""
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Dimensão fixa do vetor. Trocar de modelo com outra dimensão exige migration nova e reingestão.
EMBEDDING_DIM = 768


class Documento(Base):
    __tablename__ = "documento"
    __table_args__ = (UniqueConstraint("caminho_origem", name="uq_documento_caminho_origem"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[str] = mapped_column(String(20), index=True)  # glossario | metodologia | cultura | satelite
    fonte: Mapped[str | None] = mapped_column(String(200))  # quem escreveu ("Equipe Field Shift")
    url: Mapped[str | None] = mapped_column(String(500))
    licenca: Mapped[str | None] = mapped_column(String(60))
    idioma: Mapped[str] = mapped_column(String(5), default="pt", server_default="pt")
    caminho_origem: Mapped[str] = mapped_column(String(300))  # relativo à raiz do repositório
    hash_conteudo: Mapped[str] = mapped_column(String(64))  # sha256; reingere só se mudar
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trechos: Mapped[list["Trecho"]] = relationship(
        back_populates="documento", cascade="all, delete-orphan", order_by="Trecho.ordem"
    )


class Trecho(Base):
    __tablename__ = "trecho"
    __table_args__ = (
        # Busca vetorial aproximada por similaridade de cosseno.
        Index(
            "ix_trecho_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_trecho_tsv", "tsv", postgresql_using="gin"),
        Index("ix_trecho_metadados", "metadados", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documento.id", ondelete="CASCADE"), index=True)
    ordem: Mapped[int] = mapped_column(Integer)
    secao: Mapped[str | None] = mapped_column(String(300))  # "Glossário > Evapotranspiração"
    conteudo: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    # Busca por palavra exata ("veranico", "NDVI"); o próprio banco calcula.
    tsv: Mapped[Any] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('portuguese'::regconfig, coalesce(secao,'') || ' ' || conteudo)", persisted=True),
    )
    tokens: Mapped[int | None] = mapped_column(Integer)
    metadados: Mapped[Any] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))

    documento: Mapped[Documento] = relationship(back_populates="trechos")
