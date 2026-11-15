"""Cache da declividade por ponto (SRTM)."""
from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RelevoPonto(Base):
    """Declividade de um ponto. A chave é "<lat>_<lon>" com 4 casas (~11 m); só guarda resposta do SRTM."""

    __tablename__ = "relevo_ponto"

    chave: Mapped[str] = mapped_column(String(24), primary_key=True)
    declividade_pct: Mapped[float] = mapped_column(Float)
    classe: Mapped[str] = mapped_column(String(20))
    fonte: Mapped[str] = mapped_column(String(100))
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
