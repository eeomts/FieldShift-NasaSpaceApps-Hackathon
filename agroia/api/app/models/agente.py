"""Registro das buscas do agente na base de conhecimento."""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class BuscaLog(Base):
    """Cada busca no RAG: as palavras do produtor e a consulta reescrita (auditoria e expressões regionais)."""

    __tablename__ = "busca_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    expressao_original: Mapped[str | None] = mapped_column(Text)
    consulta: Mapped[str] = mapped_column(Text)
    filtros: Mapped[Any | None] = mapped_column(JSONB)
    trechos_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list, server_default=text("'{}'"))
    notas: Mapped[list[float]] = mapped_column(ARRAY(Float), default=list, server_default=text("'{}'"))
    descartados: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # abaixo da similaridade mínima
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
