"""Acesso ao banco do clima: célula da grade e os meses agregados."""
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import ClimaCelula, ClimaMensal

LINHAS_POR_INSERT = 500
CHAVE_MENSAL = ("celula_id", "ano", "mes")


class ClimaRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def celula_por_id(self, celula_id: str) -> ClimaCelula | None:
        return self.db.get(ClimaCelula, celula_id)

    def gravar(self, celula: dict, meses: list[dict]) -> ClimaCelula:
        """Grava a célula e seus meses (insere ou atualiza) numa transação só. Cada mês é um dict sem `celula_id`."""
        stmt = insert(ClimaCelula).values(**celula)
        self.db.execute(
            stmt.on_conflict_do_update(
                index_elements=[ClimaCelula.id],
                set_={c: stmt.excluded[c] for c in celula if c != "id"} | {"atualizado_em": func.now()},
            )
        )
        for i in range(0, len(meses), LINHAS_POR_INSERT):
            valores = [{"celula_id": celula["id"], **m} for m in meses[i : i + LINHAS_POR_INSERT]]
            ins = insert(ClimaMensal).values(valores)
            self.db.execute(
                ins.on_conflict_do_update(
                    index_elements=[getattr(ClimaMensal, c) for c in CHAVE_MENSAL],
                    set_={c: ins.excluded[c] for c in valores[0] if c not in CHAVE_MENSAL},
                )
            )
        self.db.commit()
        self.db.expire_all()
        return self.db.get(ClimaCelula, celula["id"])

    def meses(self, celula_id: str, ano: int | None = None) -> list[ClimaMensal]:
        consulta = select(ClimaMensal).where(ClimaMensal.celula_id == celula_id)
        if ano is not None:
            consulta = consulta.where(ClimaMensal.ano == ano)
        return list(self.db.scalars(consulta.order_by(ClimaMensal.ano, ClimaMensal.mes)))
