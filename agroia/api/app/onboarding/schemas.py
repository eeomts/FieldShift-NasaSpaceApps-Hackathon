"""Formato das respostas do questionário (docs/.../application/ONBOARDING.md).

Tudo é opcional: o produtor pode salvar no meio e voltar depois.
"""
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app import base

SNS = Literal["sim", "nao", "nao_sei"]
Mes = int


class Local(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    nome: str | None = Field(default=None, max_length=200)


class ItemCalendario(BaseModel):
    cultura_id: str | None = None
    texto_original: str = Field(max_length=200)
    inicio_mes: Mes | None = Field(default=None, ge=1, le=12)
    fim_mes: Mes | None = Field(default=None, ge=1, le=12)
    perene: bool = False
    consorcio_com: list[str] = Field(default_factory=list, max_length=5)
    ocupa: Literal["todo", "parte"] | None = None

    @field_validator("cultura_id")
    @classmethod
    def cultura_existe(cls, v: str | None) -> str | None:
        if v is not None and v not in base.culturas():
            raise ValueError(f"cultura desconhecida: {v}")
        return v


class Perda(BaseModel):
    resposta: SNS | None = None
    ano: int | None = Field(default=None, ge=1950, le=2100)


class Perdas(BaseModel):
    geada: Perda = Perda()
    chuva_forte: Perda = Perda()
    calor: Perda = Perda()
    seca: Perda = Perda()


class CulturaExcluida(BaseModel):
    cultura_id: str | None = None
    texto_original: str = Field(max_length=200)
    motivo: Literal["mercado", "costume", "deu_errado", "outro"] | None = None

    @field_validator("cultura_id")
    @classmethod
    def cultura_existe(cls, v: str | None) -> str | None:
        if v is not None and v not in base.culturas():
            raise ValueError(f"cultura desconhecida: {v}")
        return v


class Equipamento(BaseModel):
    equipamento_id: str | None = None
    texto_original: str = Field(max_length=200)

    @field_validator("equipamento_id")
    @classmethod
    def equipamento_existe(cls, v: str | None) -> str | None:
        if v is not None and v not in base.equipamentos():
            raise ValueError(f"equipamento desconhecido: {v}")
        return v


Prioridade = Literal["agua", "terra", "erosao", "renda", "animais", "pragas"]
Cor = Literal["escura", "marrom", "vermelha", "amarela", "cinza", "clara", "nao_sei"]
Jeito = Literal["solta", "fofa", "gruda", "torroes", "racha", "pedras", "nao_sei"]


class Respostas(BaseModel):
    # Bloco 1: quem é você
    q1_quem: Literal["produtor", "tecnico"] | None = None
    q2_area: Literal["ate_2", "2_20", "20_200", "200_1000", "mais_1000"] | None = None
    q3_tecnico: Literal["sim", "as_vezes", "nao"] | None = None
    q4_animais: Literal["sim", "nao"] | None = None
    # Bloco 2: o campo
    q5_local: Local | None = None
    q6_irrigacao: Literal["sim", "parte", "nao"] | None = None
    q7_terreno: Literal["plano", "leve", "inclinado"] | None = None
    # Bloco 3: o que você planta
    q8_texto: str | None = Field(default=None, max_length=1000)
    q8_culturas: list[ItemCalendario] = Field(default_factory=list, max_length=20)
    q9_meses_vazios: SNS | None = None  # "Nesses meses o campo fica sem nada?"
    q10_pos_colheita: Literal["parado", "pasto", "outra", "cobertura"] | None = None
    q11_palha: SNS | None = None
    # Bloco 4: solo
    q12_analise: SNS | None = None
    q12_tem_resultado: SNS | None = None
    q12_ano: int | None = Field(default=None, ge=1950, le=2100)
    q13_textura: Literal["arenosa", "media", "argilosa", "nao_sei"] | None = None
    q14_encharca: SNS | None = None
    q15_casca: SNS | None = None
    q16_erosao: SNS | None = None
    q17_dura: SNS | None = None
    q18_minhocas: SNS | None = None
    q19_cor: Cor | None = None
    q19_jeito: Jeito | None = None
    q20_partes_piores: SNS | None = None
    q21_calcario: SNS | None = None
    q22_adubo: SNS | None = None
    # Bloco 5: clima
    q23_chuva_mudou: SNS | None = None
    q24_perdas: Perdas = Perdas()
    # Bloco 6: prioridades
    q25_prioridades: list[Prioridade] = Field(default_factory=list, max_length=3)
    q26a_texto: str | None = Field(default=None, max_length=1000)
    q26a_excluidas: list[CulturaExcluida] = Field(default_factory=list, max_length=20)
    q26b_texto: str | None = Field(default=None, max_length=1000)
    q26b_equipamentos: list[Equipamento] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def prioridades_unicas(self) -> "Respostas":
        if len(set(self.q25_prioridades)) != len(self.q25_prioridades):
            raise ValueError("prioridades repetidas")
        return self
