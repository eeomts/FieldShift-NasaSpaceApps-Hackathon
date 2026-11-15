"""Rotas do chat: conversas do usuário e envio de mensagem ao assistente."""
from fastapi import APIRouter, Depends, Response, status

from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.chat import ConversaOut, ConversaResumo, EnviarMensagem, MensagemOut
from app.services.agente.agente_service import AgenteService
from app.services.conversa_service import ConversaService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversas", response_model=list[ConversaResumo])
def listar(u: Usuario = Depends(usuario_atual), servico: ConversaService = Depends()) -> list[ConversaResumo]:
    return servico.listar(u)


@router.post("/conversas", response_model=ConversaResumo, status_code=status.HTTP_201_CREATED)
def criar(u: Usuario = Depends(usuario_atual), servico: ConversaService = Depends()) -> ConversaResumo:
    return servico.criar(u)


@router.get("/conversas/{conversa_id}", response_model=ConversaOut)
def abrir(conversa_id: int, u: Usuario = Depends(usuario_atual), servico: ConversaService = Depends()) -> ConversaOut:
    return servico.abrir(u, conversa_id)


@router.post("/conversas/{conversa_id}/mensagens", response_model=MensagemOut)
def enviar(
    conversa_id: int, dados: EnviarMensagem, u: Usuario = Depends(usuario_atual), agente: AgenteService = Depends()
) -> MensagemOut:
    """A resposta do assistente (o agente roda aqui, de uma vez)."""
    return agente.responder(u, conversa_id, dados.mensagem, dados.idioma)


@router.delete("/conversas/{conversa_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar(conversa_id: int, u: Usuario = Depends(usuario_atual), servico: ConversaService = Depends()) -> Response:
    servico.apagar(u, conversa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
