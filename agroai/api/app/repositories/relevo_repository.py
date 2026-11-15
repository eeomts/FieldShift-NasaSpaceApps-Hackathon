"""Acesso ao banco do cache de declividade por ponto."""
from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import RelevoPonto


class RelevoRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def por_chave(self, chave: str) -> RelevoPonto | None:
        return self.db.get(RelevoPonto, chave)

    def gravar(self, chave: str, declividade_pct: float, classe: str, fonte: str) -> None:
        stmt = insert(RelevoPonto).values(chave=chave, declividade_pct=declividade_pct, classe=classe, fonte=fonte)
        self.db.execute(
            stmt.on_conflict_do_update(
                index_elements=[RelevoPonto.chave],
                set_={"declividade_pct": declividade_pct, "classe": classe, "fonte": fonte, "atualizado_em": func.now()},
            )
        )
        self.db.commit()
