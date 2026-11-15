"""Acesso ao banco para a fazenda (≈ Repository)."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Fazenda


class FazendaRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def salvar(self, fazenda: Fazenda) -> Fazenda:
        self.db.add(fazenda)
        self.db.commit()
        self.db.refresh(fazenda)
        return fazenda
