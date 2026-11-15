"""Acesso ao banco das conversas do chat: sempre filtrado pelo dono (usuario_id)."""
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Conversa, Mensagem


class ConversaRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def listar(self, usuario_id: UUID) -> list[Conversa]:
        consulta = select(Conversa).where(Conversa.usuario_id == usuario_id)
        return list(self.db.scalars(consulta.order_by(Conversa.atualizada_em.desc(), Conversa.id.desc())))

    def obter(self, usuario_id: UUID, conversa_id: int) -> Conversa | None:
        return self.db.scalar(select(Conversa).where(Conversa.id == conversa_id, Conversa.usuario_id == usuario_id))

    def criar(self, usuario_id: UUID) -> Conversa:
        conversa = Conversa(usuario_id=usuario_id)
        self.db.add(conversa)
        self.db.commit()
        self.db.refresh(conversa)
        return conversa

    def apagar(self, conversa: Conversa) -> None:
        self.db.delete(conversa)
        self.db.commit()

    def visiveis(self, conversa_id: int) -> list[Mensagem]:
        consulta = select(Mensagem).where(Mensagem.conversa_id == conversa_id, Mensagem.visivel.is_(True))
        return list(self.db.scalars(consulta.order_by(Mensagem.id)))

    def para_historico(self, conversa_id: int, limite_visiveis: int) -> list[Mensagem]:
        """As últimas `limite_visiveis` mensagens visíveis e os turnos de ferramenta entre elas, em ordem."""
        ids_visiveis = self.db.scalars(
            select(Mensagem.id)
            .where(Mensagem.conversa_id == conversa_id, Mensagem.visivel.is_(True))
            .order_by(Mensagem.id.desc())
            .limit(limite_visiveis)
        ).all()
        if not ids_visiveis:
            return []
        consulta = select(Mensagem).where(Mensagem.conversa_id == conversa_id, Mensagem.id >= min(ids_visiveis))
        return list(self.db.scalars(consulta.order_by(Mensagem.id)))

    def gravar_rodada(
        self, conversa: Conversa, mensagens: list[Mensagem], titulo: str | None, agora: datetime
    ) -> list[Mensagem]:
        """Grava os turnos de uma rodada completa numa transação só (rodada que falha não deixa nada)."""
        conversa.atualizada_em = agora
        if titulo and conversa.titulo is None:
            conversa.titulo = titulo
        for m in mensagens:
            m.conversa_id = conversa.id
        self.db.add_all(mensagens)
        self.db.commit()
        return mensagens
