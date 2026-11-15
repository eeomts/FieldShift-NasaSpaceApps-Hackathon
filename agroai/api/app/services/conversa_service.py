"""Conversas do usuário: criar, listar, abrir e apagar (o agente grava as mensagens)."""
from fastapi import Depends

from app.core.erros import ErroDeNegocio
from app.models import Conversa, Mensagem, Usuario
from app.repositories.conversa_repository import ConversaRepository
from app.schemas.chat import ConversaOut, ConversaResumo, Fonte, MensagemOut

TAMANHO_TITULO = 60


def titulo_da_pergunta(texto: str) -> str:
    """Primeiros ~60 caracteres, cortados no fim de uma palavra."""
    limpo = " ".join(texto.split())
    if len(limpo) <= TAMANHO_TITULO:
        return limpo
    corte = limpo[:TAMANHO_TITULO]
    if limpo[TAMANHO_TITULO] != " " and " " in corte:  # não cortou no fim de uma palavra: recua até o último espaço
        corte = corte.rsplit(" ", 1)[0]
    return corte.rstrip(" ,;:.-")


def mensagem_para_saida(m: Mensagem) -> MensagemOut:
    return MensagemOut(
        id=m.id,
        papel="produtor" if m.papel == "user" else "assistente",
        texto=m.texto or "",
        fontes=[Fonte.model_validate(f) for f in m.fontes or []],
        ferramentas_usadas=list(m.ferramentas_usadas or []),
        criada_em=m.criada_em,
    )


class ConversaService:
    def __init__(self, conversas: ConversaRepository = Depends()):
        self.conversas = conversas

    def obter_do_usuario(self, u: Usuario, conversa_id: int) -> Conversa:
        """404 igual para conversa inexistente e de outro usuário: não revela que ela existe."""
        conversa = self.conversas.obter(u.id, conversa_id)
        if conversa is None:
            raise ErroDeNegocio(404, "Conversa não encontrada.")
        return conversa

    def listar(self, u: Usuario) -> list[ConversaResumo]:
        return [ConversaResumo.model_validate(c, from_attributes=True) for c in self.conversas.listar(u.id)]

    def criar(self, u: Usuario) -> ConversaResumo:
        return ConversaResumo.model_validate(self.conversas.criar(u.id), from_attributes=True)

    def abrir(self, u: Usuario, conversa_id: int) -> ConversaOut:
        conversa = self.obter_do_usuario(u, conversa_id)
        resumo = ConversaResumo.model_validate(conversa, from_attributes=True)
        mensagens = [mensagem_para_saida(m) for m in self.conversas.visiveis(conversa.id)]
        return ConversaOut(**resumo.model_dump(), mensagens=mensagens)

    def apagar(self, u: Usuario, conversa_id: int) -> None:
        self.conversas.apagar(self.obter_do_usuario(u, conversa_id))
