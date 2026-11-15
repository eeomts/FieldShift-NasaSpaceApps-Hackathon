#!/bin/sh
# Aplica as migrations pendentes antes de servir; se falhar, o container cai e o restart tenta de novo.

set -eu

alembic upgrade head

# base de conhecimento do chat: só reprocessa o que mudou; sem chave ou com o Gemini fora, a API sobe assim mesmo
python -m app.cli.rag ingerir || echo "aviso: ingestao da base de conhecimento falhou; a API sobe sem atualizar o RAG" >&2

exec "$@"
