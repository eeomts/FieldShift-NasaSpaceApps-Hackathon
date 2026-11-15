# How It Works

The flow from the farmer's answers to the rotation comparison, and the system architecture.

Last updated: 2026-11-15

## The farmer's journey

```
1. Questionnaire  ->  2. Data collection  ->  3. Analysis engine  ->  4. Dashboard + comparison  ->  5. Chat
   (farm, crops,       (NASA + soil +         (soil portrait,         (what the farmer sees)        (plain-language
    soil, priorities)   climate, by location)  rotation scoring)                                     answers)
```

1. **Questionnaire.** The farmer marks the farm on a map and answers about crops and planting months, soil observations (with reference photos), equipment, irrigation, animals and up to 3 priorities. "I don't know" is always a valid answer.
2. **Data collection.** From the location, the back-end fetches:
   - climate history and daily data from **NASA POWER**;
   - slope from **SRTM**;
   - soil properties from **SoilGrids**;
   - the 7-day forecast from **Open-Meteo** (NASA does not publish forecasts).
3. **Analysis engine.** Builds the soil portrait (evidence fusion), filters infeasible crops and scores each rotation on 6 criteria, weighted by the farmer's priorities. See [Methodology](04-methodology.md).
4. **Dashboard and comparison.** Cards for land, climate and forecast; the current rotation side by side with the 2 best alternatives, each with why, evidence, risks, confidence and gaps.
5. **Chat.** The AgroAI assistant calls the same back-end tools (climate, crop info, rotation comparison, knowledge base) and explains the results in plain language, citing the source.

## Architecture

```
            +------------------------------+
 Farmer --> |  Web app (React + Vite, TS)  |   PT / EN, mobile first, Leaflet map
            +--------------+---------------+
                           | REST (JSON, JWT)
            +--------------v---------------+
            |  API (Python, FastAPI)       |
            |  +- onboarding + profile     |
            |  +- climate (POWER, ET0)     |--> NASA POWER API
            |  +- soil portrait            |--> SoilGrids (ISRIC)
            |  +- relief                   |--> SRTM 30 m (OpenTopoData)
            |  +- rotation engine          |    rules + formulas, no AI
            |  +- forecast                 |--> Open-Meteo
            |  +- chat agent + RAG         |--> Gemini (text only, no numbers)
            +--------------+---------------+
            +--------------v---------------+
            |  PostgreSQL 17 + pgvector    |   farms, answers, chat, knowledge base
            +------------------------------+
```

## Two interfaces

| | `agroai/web` (full) | `agroai/web-demo` (presentation) |
|---|---|---|
| Purpose | Real use | Demo for the judges |
| Sign-in | E-mail and password | Name only |
| Questionnaire | Blank | Pre-filled with a Corn Belt (Iowa) farm, with a **Skip All** button |
| Online | https://agroai.mateusmoreira.dev | https://demo-agroai.mateusmoreira.dev |

Both use the same API and database.

## Tech stack

| Layer | Technology |
|---|---|
| Front-end | React, Vite, TypeScript, Tailwind CSS, Leaflet |
| Back-end | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2, httpx |
| Database | PostgreSQL 17 with pgvector |
| Auth | argon2 password hashing + JWT |
| AI | Google Gemini (`google-genai`): free-text reading, chat, embeddings |
| Tests | pytest |
| Deploy | Docker Compose + Caddy |

## Repository map

```
agroai/api        back-end (FastAPI)
agroai/web        full web app
agroai/web-demo   presentation web app
agroai/base       crop and equipment lists for the questionnaire (single source)
data/             prepared data: crop catalogs (BR, US), demo points, knowledge base texts, ZARC, PAM, NASS
docs/             this documentation
```
