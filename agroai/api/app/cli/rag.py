"""Comandos da base de conhecimento (rode de dentro de agroai/api).

    python -m app.cli.rag ingerir [--forcar]
    python -m app.cli.rag buscar "texto" [--tipo glossario]
"""
import argparse
import logging

from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.repositories.conhecimento_repository import ConhecimentoRepository
from app.services.agente.busca_conhecimento_service import BuscaConhecimentoService
from app.services.rag.embeddings import get_embedder
from app.services.rag.ingestao import IngestaoService


def ingerir(forcar: bool) -> None:
    with Session(get_engine(), expire_on_commit=False) as db:
        for r in IngestaoService(ConhecimentoRepository(db), get_embedder()).ingerir(forcar=forcar):
            print(f"{r.situacao:24} {r.trechos:4} trechos  {r.caminho}")


def buscar(consulta: str, tipo: str | None) -> None:
    with Session(get_engine(), expire_on_commit=False) as db:
        servico = BuscaConhecimentoService(ConhecimentoRepository(db), get_embedder())
        trechos = servico.buscar(consulta, expressao_original=consulta, tipo=tipo)
    if not trechos:
        print("Nada relevante encontrado.")
    for t in trechos:
        palavra = "sim" if t.achado_por_palavra else "não"
        print(f"\n[nota {t.nota:.4f} | similaridade {t.similaridade:.3f} | palavra exata: {palavra}]")
        print(f"{t.documento_titulo} > {t.secao}")
        print(t.conteudo[:400] + ("..." if len(t.conteudo) > 400 else ""))


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="aviso: %(message)s")
    parser = argparse.ArgumentParser(description="Base de conhecimento do agente (RAG)")
    sub = parser.add_subparsers(dest="comando", required=True)
    p_ingerir = sub.add_parser("ingerir", help="grava as fontes no banco (só o que mudou)")
    p_ingerir.add_argument("--forcar", action="store_true", help="regrava mesmo sem mudança")
    p_buscar = sub.add_parser("buscar", help="testa uma busca")
    p_buscar.add_argument("consulta")
    p_buscar.add_argument("--tipo", default=None)

    args = parser.parse_args()
    try:
        if args.comando == "ingerir":
            ingerir(args.forcar)
        else:
            buscar(args.consulta, args.tipo)
    except RuntimeError as e:  # ex.: GEMINI_API_KEY não configurada
        raise SystemExit(f"erro: {e}")


if __name__ == "__main__":
    main()
