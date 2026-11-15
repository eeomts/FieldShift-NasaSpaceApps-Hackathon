# AgroAI | Field Shift

**Crop-rotation decision support for small and mid-size farmers, powered by NASA Earth observations.**

Built for the **NASA Space Apps Challenge 2026**, challenge **Field Shift: Adapting Farms with NASA Data**.

**Demo video:** [TODO: public link]  |  **Documentation:** [`docs/`](docs/README.md)  |  [Leia em portugues](README.pt-BR.md)

---

## The problem

Shifting temperatures, irregular rain, water shortages and declining soil health make it hard for farmers to choose **what to plant and when**. NASA has decades of free data about every field on Earth, but it is spread across portals, in technical formats, and out of reach for most farmers.

## What AgroAI does

A mobile-first website, in English and Portuguese, for farmers in Brazil and the United States:

1. **Short questionnaire** about the farm, the crops, what the farmer knows about the soil, and the farmer's priorities.
2. **Dashboard** with the farm's climate history (NASA POWER), terrain slope (SRTM), a soil portrait (SoilGrids + the farmer's observations) and the forecast.
3. **Rotation comparison:** the current rotation vs. the 2 best alternatives, each with *why it was suggested, evidence, benefits, risks, confidence and information gaps*.
4. **Chat assistant** that answers "what if" questions in plain language and cites the source of every number.

> AgroAI **supports, it does not decide**. Every number has a source, and the AI never computes or invents a number. The final word belongs to the farmer and the local expert.

## NASA data

| Dataset | Used for |
|---|---|
| **NASA POWER** | 1991-2020 climate normals, frost, heat, heavy rain, dry spells, evapotranspiration (FAO-56) |
| **SRTM 30 m** | Field slope for the erosion score |

Also used: **SoilGrids** (soil properties) and **Open-Meteo** (7-day forecast, since NASA does not publish forecasts). Soil moisture (SMAP), NDVI (MODIS, VIIRS) and satellite rain (GPM IMERG) are **not part of this version**.

Details in [NASA Data](docs/03-nasa-data.md). How the scores are built: [Methodology](docs/04-methodology.md).

## Run it

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 20+, Docker.

```bash
docker run -d --name agroai-dev -p 127.0.0.1:55432:5432 \
  -e POSTGRES_USER=agricultura_app -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=agricultura \
  pgvector/pgvector:pg17

cd agroai/api && uv sync
env $(grep -v '^#' .env.dev) uv run alembic upgrade head
env $(grep -v '^#' .env.dev) uv run uvicorn app.main:app --reload --port 8000

# in another terminal
cd agroai/web-demo && npm install && npm run dev   # http://localhost:5174
```

Optional key (Gemini) and tests: [Run Locally](docs/08-run-locally.md).

## Documentation

| | |
|---|---|
| [Overview](docs/01-overview.md) | Problem, users, solution, how it answers the challenge |
| [How It Works](docs/02-how-it-works.md) | Farmer's journey, architecture, stack |
| [NASA Data](docs/03-nasa-data.md) | Each dataset, version, resolution and use |
| [Methodology](docs/04-methodology.md) | Rotation comparison and where every number comes from |
| [Limitations and Roadmap](docs/05-limitations-roadmap.md) | What works, what is partial, what is next |
| [References](docs/06-references.md) | Other data, libraries, images, licenses |
| [Use of AI](docs/07-ai-use.md) | AI in the product, in development and in media |

## Tech stack

React, Vite, TypeScript, Tailwind CSS, Leaflet, Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL + pgvector, Google Gemini (language only), Docker

## Use of AI

- **Code:** developed with AI assistance (Claude Code, Anthropic), reviewed and tested by the team.
- **Demo video:** edited with AI tools, with a visible watermark.
- **Product:** Google Gemini reads free text and powers the chat. It never computes or invents numbers.

Full statement: [Use of AI](docs/07-ai-use.md).

## Team

[TODO: team name and members]
