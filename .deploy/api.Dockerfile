# API do AgroIA (FastAPI). Contexto do build: a raiz do repositório; o container tem o mesmo layout do repo sob /app.
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.2 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/agroia/api/.venv/bin:$PATH"

WORKDIR /app/agroia/api

# dependências primeiro: só reinstala quando o uv.lock muda
COPY agroia/api/pyproject.toml agroia/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY agroia/api/ ./
COPY agroia/base/ /app/agroia/base/
COPY data/catalogo/ /app/data/catalogo/
COPY data/rag/ /app/data/rag/
COPY data/demo/pontos_demo.csv /app/data/demo/pontos_demo.csv

RUN useradd --system --no-create-home agroia && chown -R agroia /app
USER agroia

COPY --chmod=755 --from=deploy api-entrypoint.sh /usr/local/bin/entrypoint

EXPOSE 8000
ENTRYPOINT ["entrypoint"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
