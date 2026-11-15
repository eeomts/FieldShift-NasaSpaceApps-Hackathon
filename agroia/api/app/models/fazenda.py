"""Fazenda e calendário do produtor (onboarding)."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Fazenda(Base):
    __tablename__ = "fazenda"
    __table_args__ = (
        CheckConstraint("lat IS NULL OR (lat BETWEEN -90 AND 90)", name="ck_fazenda_lat"),
        CheckConstraint("lon IS NULL OR (lon BETWEEN -180 AND 180)", name="ck_fazenda_lon"),
        CheckConstraint("perfil IS NULL OR perfil IN ('A','B','C')", name="ck_fazenda_perfil"),
        CheckConstraint("papel IS NULL OR papel IN ('produtor','tecnico')", name="ck_fazenda_papel"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"), unique=True)

    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    nome_local: Mapped[str | None] = mapped_column(String(200))
    perfil: Mapped[str | None] = mapped_column(String(1))  # nível de dado do solo: A, B ou C
    papel: Mapped[str | None] = mapped_column(String(10))  # quem respondeu: produtor ou tecnico
    irrigacao: Mapped[str | None] = mapped_column(String(10))
    animais: Mapped[bool | None] = mapped_column(Boolean)
    terreno: Mapped[str | None] = mapped_column(String(20))
    prioridades: Mapped[list] = mapped_column(JSONB, default=list)
    culturas_excluidas: Mapped[list] = mapped_column(JSONB, default=list)
    equipamentos: Mapped[list] = mapped_column(JSONB, default=list)
    retrato_solo: Mapped[dict] = mapped_column(JSONB, default=dict)
    proximos_passos: Mapped[list] = mapped_column(JSONB, default=list)

    respostas: Mapped[dict] = mapped_column(JSONB, default=dict)
    passo_atual: Mapped[int] = mapped_column(Integer, default=0)
    onboarding_concluido: Mapped[bool] = mapped_column(Boolean, default=False)
    status_processamento: Mapped[str] = mapped_column(String(20), default="pendente")

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="fazenda")
    calendario: Mapped[list["CalendarioItem"]] = relationship(
        back_populates="fazenda", cascade="all, delete-orphan", order_by="CalendarioItem.ordem"
    )


class CalendarioItem(Base):
    """Uma cultura do calendário atual, já confirmada pelo produtor (pergunta 8)."""

    __tablename__ = "calendario_item"
    __table_args__ = (
        CheckConstraint("inicio_mes IS NULL OR inicio_mes BETWEEN 1 AND 12", name="ck_cal_inicio"),
        CheckConstraint("fim_mes IS NULL OR fim_mes BETWEEN 1 AND 12", name="ck_cal_fim"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fazenda_id: Mapped[UUID] = mapped_column(ForeignKey("fazenda.id", ondelete="CASCADE"), index=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0)
    cultura_id: Mapped[str | None] = mapped_column(String(40))  # None = fora da base ("sem parâmetros")
    texto_original: Mapped[str] = mapped_column(Text)
    inicio_mes: Mapped[int | None] = mapped_column(Integer)
    fim_mes: Mapped[int | None] = mapped_column(Integer)
    perene: Mapped[bool] = mapped_column(Boolean, default=False)
    consorcio_com: Mapped[list] = mapped_column(JSONB, default=list)
    ocupa: Mapped[str | None] = mapped_column(String(10))  # 'todo' | 'parte'

    fazenda: Mapped[Fazenda] = relationship(back_populates="calendario")
