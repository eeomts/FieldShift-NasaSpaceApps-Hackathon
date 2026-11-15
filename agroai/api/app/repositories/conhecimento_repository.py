"""Acesso ao banco da base de conhecimento: documentos, trechos e a busca híbrida.

A busca combina duas listas por Reciprocal Rank Fusion (RRF): a vetorial (mesmo significado,
distância de cosseno) e a textual (mesmas palavras, full-text em português). Cada trecho ganha
1 / (RRF_K + posição) em cada lista em que aparece, e as notas se somam.
"""
from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy import cast, delete, func, select, union
from sqlalchemy.dialects.postgresql import REGCONFIG
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import BuscaLog, Documento, Trecho

RRF_K = 60
CANDIDATOS_POR_BUSCA = 30


@dataclass
class TrechoEncontrado:
    trecho_id: int
    documento_titulo: str
    documento_tipo: str
    fonte: str | None
    url: str | None
    secao: str | None
    conteudo: str
    nota: float  # nota combinada (RRF)
    similaridade: float  # cosseno entre a consulta e o trecho (1 = idêntico)
    achado_por_palavra: bool  # a busca textual também achou o trecho


class ConhecimentoRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # --- documentos ---

    def documento_por_caminho(self, caminho: str) -> Documento | None:
        return self.db.scalar(select(Documento).where(Documento.caminho_origem == caminho))

    def remover_documentos_fora_de(self, caminhos: list[str]) -> list[str]:
        """Apaga (com os trechos) os documentos cujo caminho não está na lista; devolve os caminhos apagados."""
        apagados = self.db.scalars(
            delete(Documento).where(Documento.caminho_origem.not_in(caminhos)).returning(Documento.caminho_origem)
        ).all()
        self.db.commit()
        return list(apagados)

    def salvar_documento(self, documento: Documento) -> Documento:
        self.db.add(documento)
        self.db.commit()
        return documento

    # --- busca ---

    def buscar_hibrido(
        self, consulta: str, vetor_consulta: list[float], limite: int = 5, tipo: str | None = None
    ) -> list[TrechoEncontrado]:
        filtros = [Documento.tipo == tipo] if tipo else []

        distancia = Trecho.embedding.cosine_distance(vetor_consulta)
        vetorial = (
            select(Trecho.id.label("id"), func.row_number().over(order_by=distancia).label("posicao"))
            .join(Documento)
            .where(*filtros)
            .order_by(distancia)
            .limit(CANDIDATOS_POR_BUSCA)
            .subquery("vetorial")
        )

        # websearch_to_tsquery aceita texto livre (aspas, OR, -palavra) sem estourar com símbolos.
        tsquery = func.websearch_to_tsquery(cast("portuguese", REGCONFIG), consulta)
        relevancia = func.ts_rank_cd(Trecho.tsv, tsquery)
        textual = (
            select(Trecho.id.label("id"), func.row_number().over(order_by=relevancia.desc()).label("posicao"))
            .join(Documento)
            .where(Trecho.tsv.op("@@")(tsquery), *filtros)
            .order_by(relevancia.desc())
            .limit(CANDIDATOS_POR_BUSCA)
            .subquery("textual")
        )

        ids = union(select(vetorial.c.id), select(textual.c.id)).subquery("ids")
        nota = func.coalesce(1.0 / (RRF_K + vetorial.c.posicao), 0) + func.coalesce(1.0 / (RRF_K + textual.c.posicao), 0)
        final = (
            select(Trecho, Documento, (1 - distancia).label("similaridade"), textual.c.posicao, nota.label("nota"))
            .join(ids, ids.c.id == Trecho.id)
            .join(Documento, Documento.id == Trecho.documento_id)
            .outerjoin(vetorial, vetorial.c.id == Trecho.id)
            .outerjoin(textual, textual.c.id == Trecho.id)
            .order_by(nota.desc(), Trecho.id)
            .limit(limite)
        )

        return [
            TrechoEncontrado(
                trecho_id=t.id,
                documento_titulo=d.titulo,
                documento_tipo=d.tipo,
                fonte=d.fonte,
                url=d.url,
                secao=t.secao,
                conteudo=t.conteudo,
                nota=float(n),
                similaridade=float(sim),
                achado_por_palavra=pos_textual is not None,
            )
            for t, d, sim, pos_textual, n in self.db.execute(final)
        ]

    def registrar_busca(self, log: BuscaLog) -> BuscaLog:
        self.db.add(log)
        self.db.commit()
        return log
