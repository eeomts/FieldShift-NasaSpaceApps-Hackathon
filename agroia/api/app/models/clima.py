"""Clima do NASA POWER guardado por célula da grade e agregado por mês."""
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, ForeignKey, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ClimaCelula(Base):
    """Uma célula da grade (~50 km). O id é "<lat>_<lon>" do centro; fazendas vizinhas dividem a mesma linha."""

    __tablename__ = "clima_celula"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    elevacao_m: Mapped[float | None] = mapped_column(Float)  # elevação da célula, vinda do POWER
    inicio: Mapped[date] = mapped_column(Date)  # período baixado
    fim: Mapped[date] = mapped_column(Date)
    limite_chuva_forte_mm: Mapped[float | None] = mapped_column(Float)  # percentil 95 dos dias com chuva, 1991-2020
    fonte: Mapped[str] = mapped_column(String(100))
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ClimaMensal(Base):
    """Uma linha por célula, ano e mês. Valor sem dado é NULL, nunca 0."""

    __tablename__ = "clima_mensal"
    __table_args__ = (CheckConstraint("mes BETWEEN 1 AND 12", name="ck_clima_mensal_mes"),)

    celula_id: Mapped[str] = mapped_column(ForeignKey("clima_celula.id", ondelete="CASCADE"), primary_key=True)
    ano: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    mes: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    chuva_mm: Mapped[float | None] = mapped_column(Float)
    et0_mm: Mapped[float | None] = mapped_column(Float)
    tmed_c: Mapped[float | None] = mapped_column(Float)
    tmax_media_c: Mapped[float | None] = mapped_column(Float)
    tmin_media_c: Mapped[float | None] = mapped_column(Float)
    tmax_absoluta_c: Mapped[float | None] = mapped_column(Float)
    tmin_absoluta_c: Mapped[float | None] = mapped_column(Float)
    dias_geada: Mapped[int | None] = mapped_column(SmallInteger)
    dias_calor: Mapped[int | None] = mapped_column(SmallInteger)
    dias_chuva_forte: Mapped[int | None] = mapped_column(SmallInteger)
    maior_seq_seca_dias: Mapped[int | None] = mapped_column(SmallInteger)
    dias_validos: Mapped[int | None] = mapped_column(SmallInteger)
    # Graus-dia do mês por Tb inteira ({"0": 512.3, ..., "20": 3.1}), sem teto. {} = mês sem temperatura completa;
    # NULL = célula baixada antes desta coluna (o serviço baixa de novo).
    gd_por_tb: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
