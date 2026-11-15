"""Saída da rota GET /fazenda/previsao (Open-Meteo, D-014)."""
from datetime import date

from pydantic import BaseModel

from app.schemas.chat import DataUtc


class DiaPrevisao(BaseModel):
    data: date
    tmax: float | None  # °C
    tmin: float | None  # °C
    chuva_mm: float | None
    chance_chuva: int | None  # %
    codigo_tempo: int | None  # WMO


class Previsao(BaseModel):
    fonte: str
    licenca: str
    dias: list[DiaPrevisao]
    gerado_em: DataUtc
