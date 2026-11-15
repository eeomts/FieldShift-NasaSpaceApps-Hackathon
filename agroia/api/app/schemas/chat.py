"""Entrada e saída das rotas do chat."""
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _em_utc(d: datetime) -> datetime:
    return d.astimezone(UTC)


DataUtc = Annotated[datetime, AfterValidator(_em_utc)]


class EnviarMensagem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    mensagem: str = Field(min_length=1, max_length=2000)


class Fonte(BaseModel):
    tipo: Literal["clima", "conhecimento", "cultura", "fazenda"]
    titulo: str
    detalhe: str | None = None


class MensagemOut(BaseModel):
    id: int
    papel: Literal["produtor", "assistente"]
    texto: str
    fontes: list[Fonte]
    ferramentas_usadas: list[str]
    criada_em: DataUtc


class ConversaResumo(BaseModel):
    id: int
    titulo: str | None
    criada_em: DataUtc
    atualizada_em: DataUtc


class ConversaOut(ConversaResumo):
    mensagens: list[MensagemOut]
