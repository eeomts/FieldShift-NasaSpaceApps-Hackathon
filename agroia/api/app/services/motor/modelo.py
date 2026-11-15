"""Tipos do motor de rotação: estratégia, notas, evidências e o resultado da análise."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from app.services.motor.calendario import meses_do_periodo

Origem = Literal["atual", "janela", "tolerante_seca", "leguminosa"]
Confianca = Literal["alta", "media", "baixa"]
CRITERIOS = ("agua", "terra", "erosao", "pragas", "renda", "animais")


@dataclass(frozen=True)
class ItemRotacao:
    cultura_id: str | None  # None ou fora do catálogo do motor: entra na rotação, mas sem nota própria
    inicio_mes: int | None
    fim_mes: int | None
    perene: bool
    texto: str

    def meses(self) -> list[int]:
        return meses_do_periodo(self.inicio_mes, self.fim_mes, self.perene)


@dataclass(frozen=True)
class Estrategia:
    id: str
    nome: str
    origem: Origem
    itens: tuple[ItemRotacao, ...]


@dataclass(frozen=True)
class Eliminada:
    estrategia: Estrategia
    motivos: list[str]


@dataclass(frozen=True)
class Evidencia:
    texto: str
    valor: float | str | None  # None = sem dado; texto quando for faixa ("450–800")
    unidade: str | None
    fonte: str
    periodo: str | None


@dataclass(frozen=True)
class NotaCriterio:
    criterio: str
    nota: float | None  # None = sem dado: o critério é ignorado e o peso vai para os outros
    explicacao: str
    evidencias: list[Evidencia] = field(default_factory=list)


@dataclass(frozen=True)
class Alerta:
    codigo: str
    texto: str


@dataclass
class ResultadoEstrategia:
    estrategia: Estrategia
    notas: dict[str, NotaCriterio]  # por critério, na ordem de CRITERIOS
    nota_final: float | None
    pesos: dict[str, float]  # pesos efetivos (só critérios com nota; somam 1)
    por_que: list[str]
    alertas: list[Alerta]
    confianca: Confianca
    lacunas: list[str]
    onde_piora: list[str] = field(default_factory=list)  # até 3 frases dos critérios em que perde da atual


@dataclass
class Analise:
    pais: str
    atual: ResultadoEstrategia
    melhores: list[ResultadoEstrategia]  # até 2, diferentes da atual e entre si
    eliminadas: list[Eliminada]
    pesos: dict[str, float]  # pesos das prioridades, antes de tirar critério sem dado
    fontes: list[str]
    gerado_em: datetime
    atual_e_a_melhor: bool = False  # nenhuma das melhores tem nota final maior que a da atual
