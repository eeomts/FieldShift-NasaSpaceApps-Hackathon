"""Acesso ao banco do cache do solo por ponto (uma linha por propriedade)."""
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import SoloPontoCache
from app.services.integracao.soilgrids import FONTE, PropriedadeSolo


class SoloRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def por_chave(self, chave: str) -> dict[str, PropriedadeSolo]:
        """Propriedades já guardadas do ponto (vazio se nunca foi consultado)."""
        linhas = self.db.scalars(select(SoloPontoCache).where(SoloPontoCache.chave == chave)).all()
        return {
            l.propriedade: PropriedadeSolo(l.propriedade, l.superficial, l.raizes, l.incerteza_superficial, l.incerteza_raizes, l.sem_dado)
            for l in linhas
        }

    def liberar_conexao(self) -> None:
        """Encerra a transação de leitura: a chamada lenta ao SoilGrids não pode deixar a conexão parada no banco."""
        self.db.commit()

    def gravar(self, chave: str, p: PropriedadeSolo) -> None:
        """Grava (ou atualiza) uma propriedade do ponto e confirma na hora."""
        colunas = {
            "sem_dado": p.sem_dado, "superficial": p.superficial, "raizes": p.raizes,
            "incerteza_superficial": p.incerteza_superficial, "incerteza_raizes": p.incerteza_raizes, "fonte": FONTE,
        }  # fmt: skip
        stmt = insert(SoloPontoCache).values(chave=chave, propriedade=p.nome, **colunas)
        self.db.execute(
            stmt.on_conflict_do_update(
                index_elements=[SoloPontoCache.chave, SoloPontoCache.propriedade],
                set_={**colunas, "atualizado_em": func.now()},
            )
        )
        self.db.commit()
