"""Saída da rota de estratégias de rotação (contrato do PR D3)."""
from typing import Literal

from pydantic import BaseModel

from app.schemas.chat import DataUtc

Criterio = Literal["agua", "terra", "erosao", "pragas", "renda", "animais"]


class Evidencia(BaseModel):
    texto: str
    valor: float | str | None  # texto quando for faixa ("450–800"); None = sem dado
    unidade: str | None
    fonte: str
    periodo: str | None


class ItemEstrategia(BaseModel):
    cultura_id: str | None
    nome: str
    inicio_mes: int | None
    fim_mes: int | None
    perene: bool


class NotaCriterio(BaseModel):
    criterio: Criterio
    nota: float | None
    explicacao: str
    evidencias: list[Evidencia]


class Alerta(BaseModel):
    codigo: str
    texto: str


class Resultado(BaseModel):
    id: str
    nome: str
    origem: Literal["atual", "janela", "tolerante_seca", "leguminosa"]
    itens: list[ItemEstrategia]
    nota_final: float | None  # 0 a 1
    notas: list[NotaCriterio]  # na ordem de Criterio
    por_que: list[str]
    onde_piora: list[str]
    alertas: list[Alerta]
    confianca: Literal["alta", "media", "baixa"]
    lacunas: list[str]


class Eliminada(BaseModel):
    nome: str
    motivos: list[str]


class Analise(BaseModel):
    pais: Literal["BR", "US"]
    atual_e_a_melhor: bool
    pesos: dict[Criterio, float]
    atual: Resultado
    melhores: list[Resultado]  # 0 a 2
    eliminadas: list[Eliminada]
    fontes: list[str]
    gerado_em: DataUtc
