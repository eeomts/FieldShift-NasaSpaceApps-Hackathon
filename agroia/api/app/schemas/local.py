"""Saída das rotas de local (busca de lugar e informações do ponto)."""
from typing import Literal

from pydantic import BaseModel


class LugarBusca(BaseModel):
    nome: str
    pais: str | None  # nome do país no idioma pedido
    pais_codigo: str | None  # ISO 3166-1 alfa-2 maiúsculo
    lat: float
    lon: float


class InfoLocal(BaseModel):
    hemisferio: Literal["N", "S"]
    zona_climatica: str | None  # Köppen-Geiger aproximada (NASA POWER); None se o POWER não respondeu
    lugar: str | None
    pais: str | None
    pais_codigo: str | None
    geada_no_historico: bool | None  # None se ainda não há clima diário guardado para a célula
