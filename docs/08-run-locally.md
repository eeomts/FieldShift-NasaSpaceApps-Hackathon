# Run Locally

How to run AgroAI on your own computer.

Last updated: 2026-11-15

## Requirements

Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+ and Docker.

## Steps

All commands start from the repository root.

```bash
# 0. Local database (first time only; afterwards: docker start agroai-dev)
docker run -d --name agroai-dev -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=agricultura \
  pgvector/pgvector:pg17

# 1. API (terminal 1)
cd agroai/api
uv sync
env $(grep -v '^#' .env.dev) uv run alembic upgrade head
env $(grep -v '^#' .env.dev) uv run uvicorn app.main:app --reload --port 8000

# 2. Web app (terminal 2), pick one
cd agroai/web-demo   # presentation version: http://localhost:5174 (sign in with a name, pre-filled farm)
cd agroai/web        # full version:         http://localhost:5173
npm install
npm run dev
```

## Optional keys

The app runs without keys. Each key turns on one more part:

| Variable (in `agroai/api/.env`) | Turns on | Without it |
|---|---|---|
| `GEMINI_API_KEY` | Chat assistant and free-text reading | Questionnaire uses the crop list; the chat says it is unavailable. Dashboard and rotation comparison work normally |

Use `agroai/api/.env.example` as the template. Never commit the `.env` file.

## Tests

```bash
cd agroai/api
uv run pytest
```

The tests need a local test database; see [`agroai/README.md`](../agroai/README.md).
