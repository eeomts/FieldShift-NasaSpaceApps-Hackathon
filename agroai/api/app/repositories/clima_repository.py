"""Acesso ao banco do clima: célula da grade, os meses agregados e a série diária de Tmin/Tmax."""
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import ClimaCelula, ClimaMensal, ClimaSerieDiaria

LINHAS_POR_INSERT = 500
ANOS_POR_INSERT = 50  # cada ano leva dois vetores de 365 valores
CHAVE_MENSAL = ("celula_id", "ano", "mes")
CHAVE_SERIE = ("celula_id", "ano")


class ClimaRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def celula_por_id(self, celula_id: str) -> ClimaCelula | None:
        return self.db.get(ClimaCelula, celula_id)

    def faltam_graus_dia(self, celula_id: str) -> bool:
        """Algum mês da célula sem `gd_por_tb` (baixada antes da coluna existir)."""
        consulta = select(ClimaMensal.celula_id).where(ClimaMensal.celula_id == celula_id, ClimaMensal.gd_por_tb.is_(None))
        return self.db.scalars(consulta.limit(1)).first() is not None

    def faltam_serie_diaria(self, celula: ClimaCelula) -> bool:
        """A célula não tem nenhuma linha de série diária (baixada antes da migration 0009). Ano faltando não conta."""
        consulta = select(ClimaSerieDiaria.celula_id).where(ClimaSerieDiaria.celula_id == celula.id).limit(1)
        return self.db.scalars(consulta).first() is None

    def gravar(self, celula: dict, meses: list[dict], series: list[dict] | None = None) -> ClimaCelula:
        """Grava a célula, seus meses e a série diária (insere ou atualiza) numa transação só.

        Cada mês é um dict sem `celula_id`; cada série é {"ano", "tmin_c", "tmax_c"}.
        """
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
        series = series or []
        for i in range(0, len(series), ANOS_POR_INSERT):
            valores = [{"celula_id": celula["id"], **x} for x in series[i : i + ANOS_POR_INSERT]]
            ins = insert(ClimaSerieDiaria).values(valores)
            self.db.execute(
                ins.on_conflict_do_update(
                    index_elements=[getattr(ClimaSerieDiaria, c) for c in CHAVE_SERIE],
                    set_={c: ins.excluded[c] for c in valores[0] if c not in CHAVE_SERIE},
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

    def series_diarias(self, celula_id: str) -> list[ClimaSerieDiaria]:
        """Tmin/Tmax diárias de todos os anos da célula, em ordem de ano."""
        consulta = select(ClimaSerieDiaria).where(ClimaSerieDiaria.celula_id == celula_id)
        return list(self.db.scalars(consulta.order_by(ClimaSerieDiaria.ano)))
