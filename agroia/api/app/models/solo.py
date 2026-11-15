"""Cache do solo por ponto (SoilGrids), uma linha por propriedade."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SoloPontoCache(Base):
    """Uma propriedade do SoilGrids num ponto. Chave = "<lat>_<lon>" com 3 casas (~110 m) + propriedade (clay, sand, ...).

    Cada propriedade é gravada assim que chega: se a busca falhar no meio, a próxima só pede as que faltam.
    Valores já convertidos (argila em %, carbono em g/kg, pH, ...), antes da renormalização da textura.
    Ponto sem dado no mapa (área urbana ou água) também é guardado, com sem_dado = true, para não chamar a API de novo.
    """

    __tablename__ = "solo_ponto"

    chave: Mapped[str] = mapped_column(String(24), primary_key=True)
    propriedade: Mapped[str] = mapped_column(String(12), primary_key=True)
    sem_dado: Mapped[bool] = mapped_column(Boolean, default=False)
    superficial: Mapped[float | None] = mapped_column(Float)  # média ponderada de 0 a 30 cm
    raizes: Mapped[float | None] = mapped_column(Float)  # média ponderada de 0 a 100 cm
    incerteza_superficial: Mapped[float | None] = mapped_column(Float)  # (Q0,95 − Q0,05) ÷ Q0,50
    incerteza_raizes: Mapped[float | None] = mapped_column(Float)
    fonte: Mapped[str] = mapped_column(String(100))
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
