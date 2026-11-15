# Run Locally

How to run AgroAI on your own computer. To just try it, use the live demo (no password): https://demo-agroai.mateusmoreira.dev

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
env $(grep -v '^#' .env.dev) GEMINI_API_KEY=<your-key> uv run uvicorn app.main:app --reload --port 8000
# without a Gemini key, drop "GEMINI_API_KEY=<your-key>": everything except the chat still works
```

Then, in terminal 2, pick **one** web app:

```bash
# Option A: presentation version, http://localhost:5174 (sign in with a name, pre-filled farm)
cd agroai/web-demo && npm install && npm run dev

# Option B: full version, http://localhost:5173 (e-mail and password)
cd agroai/web && npm install && npm run dev
```

## Optional keys

The app runs without keys. Each key turns on one more part:

| Variable (in `agroai/api/.env`) | Turns on | Without it |
|---|---|---|
| `GEMINI_API_KEY` | Chat assistant and free-text reading | Questionnaire uses the crop list; the chat says it is unavailable. Dashboard and rotation comparison work normally |

Use `agroai/api/.env.example` as the template. Never commit the `.env` file. Note: `.env.dev` sets `GEMINI_API_KEY` empty, and a variable set on the command line wins over `.env`, so pass the key on the command line as shown above.

## Tests

The tests use their own local PostgreSQL (port 55433, settings in `agroai/api/.env.test`). The test setup refuses to run against a database that is not local. No test calls the internet or Gemini.

```bash
# first time only
docker run -d --name agroai-teste -p 55433:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=teste -e POSTGRES_DB=agricultura \
  pgvector/pgvector:pg17

cd agroai/api
set -a; . ./.env.test; set +a; uv run alembic upgrade head
uv run pytest
```
