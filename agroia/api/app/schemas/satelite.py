"""Saída da rota GET /fazenda/satelite: o que os satélites da NASA mostram no ponto da fazenda."""
from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.schemas.chat import DataUtc


class Umidade(BaseModel):
    fonte: str
    resolucao: str
    data: date
    superficie: float  # m³/m³, 0-5 cm
    raiz: float  # m³/m³, zona das raízes (0-100 cm)
    situacao: Literal["seco", "normal", "umido"] | None
    posicao: float | None  # 0 a 1 entre os mesmos dias dos anos anteriores
    media_historica: float | None
    anos_comparados: int


class PontoNdvi(BaseModel):
    data: date
    valor: float


class Ndvi(BaseModel):
    fonte: str
    resolucao: str
    data: date
    valor: float
    situacao: Literal["descoberto", "pouco", "verde", "muito"]
    serie: list[PontoNdvi]


class DiaChuva(BaseModel):
    data: date
    mm: float


class Chuva(BaseModel):
    fonte: str
    resolucao: str
    dias: list[DiaChuva]
    total_7d: float
    total_30d: float
    maior: DiaChuva | None


class Satelite(BaseModel):
    lat: float
    lon: float
    umidade: Umidade | None
    ndvi: Ndvi | None
    chuva: Chuva | None
    # parte ("umidade", "ndvi", "chuva") -> código do motivo; o front escreve o texto no idioma do produtor
    faltas: dict[str, Literal["sem_token", "sem_permissao", "sem_dado_ponto", "nuvem", "sem_arquivo", "fora_do_ar", "erro"]]
    avisos: list[Literal["imerg_bloqueado", "imerg_indisponivel"]]
    gerado_em: DataUtc
