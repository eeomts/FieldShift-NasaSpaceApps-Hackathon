# API do AgroIA (FastAPI). Contexto do build: agroia/ (precisa de api/ e base/).
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.2 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/api/.venv/bin:$PATH"

WORKDIR /app/api

# dependências primeiro: só reinstala quando o uv.lock muda
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY api/ ./
COPY base/ /app/base/

RUN useradd --system --no-create-home agroia && chown -R agroia /app
USER agroia

COPY --chmod=755 --from=deploy api-entrypoint.sh /usr/local/bin/entrypoint

EXPOSE 8000
ENTRYPOINT ["entrypoint"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
