# Space Apps Project Submission

Text for each field of the NASA Space Apps project page, ready to copy and paste. All fields must be in English.

Last updated: 2026-11-15 | Deadline: Sunday, 2026-11-15, 11:59 p.m. (local time of the Uberlandia Local Event)

---

## Project Name

AgroAI

## High-Level Project Summary

AgroAI is a mobile-first decision-support website, in English and Portuguese, that helps small and mid-size farmers in Brazil and the United States choose healthier crop rotations. The farmer answers a short questionnaire about the farm, the current crops, what they know about the soil and their own priorities (save water, improve the soil, prevent erosion, fewer pests, extra income, animal feed). AgroAI then combines NASA Earth observations (NASA POWER climate and SRTM slope) with soil data and a sourced crop catalog to compare the current rotation with the two best alternatives. For each strategy it explains why it was suggested, the evidence, benefits, risks, confidence and information gaps, exactly what the Field Shift challenge asks for. A chat assistant answers "what if" questions in plain language and cites the source of every number. AgroAI supports, it does not decide: all scores come from transparent rules, the AI never computes or invents a number, and the final word belongs to the farmer and the local expert.

## Link to Project Demo

[TODO: public link to the 30-second video (YouTube or Google Drive, no login). If the narration is not in English, it must have English subtitles.]

## Link to Final Project

[TODO: public link to the GitHub repository]

## Detailed Project Description

**What it does.** AgroAI turns decades of free NASA data into a crop-rotation comparison a farmer can act on this season. It shows the months when the field is bare, the seasons when the current crops are more vulnerable (frost in flowering, water deficit, heavy rain on bare soil), and rotation options that fill those gaps.

**How it works.**
1. *Questionnaire:* the farmer marks the farm on a map and answers about crops and planting months, soil observations (with reference photos), equipment, irrigation and up to 3 priorities. "I don't know" is always accepted.
2. *Data collection:* from the location, the back-end reads NASA POWER (daily data and 1991-2020 normals), SRTM slope, SoilGrids soil properties and a 7-day forecast. For the Dashboard it also reads recent SMAP soil moisture, MODIS NDVI and GPM IMERG rain from NASA Earthdata.
3. *Soil portrait:* evidence fusion of lab results, field tests, the farmer's observations and SoilGrids, each with a confidence weight. When sources disagree, the app says so and trusts what the farmer sees.
4. *Rotation engine:* generates candidates (fill the bare window, swap for a drought-tolerant crop, add a legume), removes infeasible ones (growing degree days, frost in flowering, equipment, excluded crops) and scores each on 6 criteria from 0 to 1: water, soil, erosion, pests, income and animal feed. Water demand uses FAO-56 (ET0 from NASA POWER, ETc = Kc x ET0); erosion uses rainfall, SRTM slope and soil erodibility. The farmer's priorities weight the final score.
5. *Results:* the current rotation and the 2 best alternatives, each with why, evidence, risks, confidence and gaps. The chat assistant explains them and answers "what if" questions.

**Benefits.** Free NASA data becomes plain-language guidance; every recommendation is explainable and traceable to its source; the farmer's own knowledge counts; and it is built for the phone, in two languages.

**What we hope to achieve.** Help farmers adopt rotations that keep the soil covered, reduce erosion and water stress and add income, while giving agronomists a transparent tool they can check and adapt. Next steps: official planting windows (ZARC in Brazil, USDA NASS in the US), local market data, the satellite data (SMAP, NDVI, GPM IMERG) inside the analysis and the chat, and validation with extension services.

**Tools and languages.** Python (FastAPI, SQLAlchemy, Alembic, Pydantic, pytest), PostgreSQL with pgvector, TypeScript (React, Vite, Tailwind CSS, Leaflet), Docker, Google Gemini for language tasks only.

Full documentation: `docs/README.md` in the repository.

## Use of Super Intelligence (SI)

Yes. (1) The code was developed with AI assistance: the team used Claude Code (Anthropic) to help write and review code, tests, data scripts and documentation. The idea, product rules, data choices and methodology are the team's, and all code was reviewed and tested by the team. (2) The demo video was edited with AI tools [TODO: tool name] and carries a visible watermark. (3) In the product, Google Gemini reads the farmer's free-text answers, powers the chat assistant and creates embeddings for the knowledge-base search. It never computes or invents numbers: every number comes from NASA data, the crop catalog or a formula in code, and the prompt forbids the model from producing numbers on its own. No AI-generated content uses NASA branding. Details: `docs/07-ai-use.md`.

## NASA Data

- **NASA POWER** (daily point API and climatology, AG community: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M, ALLSKY_SFC_SW_DWN, WS2M): 1991-2020 rain and temperature normals, frost, heat, heavy-rain days, dry spells, growing degree days, and reference evapotranspiration (FAO-56, computed by AgroAI).
- **SRTM 30 m**: field slope (Horn method), used in the erosion score.

- **SMAP L4** (SPL4SMGP v8): surface and root-zone soil moisture today, compared with the same day in up to 8 past years. Dashboard.
- **MODIS MOD13Q1** v061: NDVI over the last 365 days (good-quality pixels only). Dashboard.
- **GPM IMERG** Late, daily v07: rain over the last 30 days. Dashboard.

SMAP, MODIS and IMERG are read live from NASA Earthdata (CMR + OPeNDAP) and shown on the Dashboard only; the rotation engine and the chat do not use them yet.

Details: `docs/03-nasa-data.md`.

## Space Agency Partner Data and Other References

We did not use data from the Space Agency Partners. Other references:

- **Data:** SoilGrids 2.0 (ISRIC, CC BY 4.0); Open-Meteo forecast (CC BY 4.0); OpenStreetMap Nominatim (ODbL); OpenTopoData (SRTM access); MAPA ZARC risk tables (Brazil); IBGE municipalities and SIDRA PAM table 5457; USDA NASS Quick Stats, Usual Planting and Harvesting Dates (Handbook 628) and Cropland Data Layer; US Census TIGERweb; FAO-56; crop parameters from Embrapa, FAO, IAPAR/IDR-Parana, USDA NRCS/ARS and university extension services.
- **Images:** soil reference photos from Wikimedia Commons (CC0, public domain, CC BY, CC BY-SA), with authors and licenses in `agroai/web/public/fotos-solo/CREDITOS.md`.
- **Code libraries:** FastAPI, Uvicorn, SQLAlchemy, psycopg, Alembic, Pydantic, argon2-cffi, PyJWT, httpx, Shapely, pgvector, google-genai, pytest, React, React Router, Leaflet, React Leaflet, Vite, TypeScript, Tailwind CSS, PostgreSQL, Docker, Caddy.
- **AI services:** Google Gemini, Claude Code.

Details: `docs/06-references.md` and `data/FONTES.md`.

---

## Checklist before "Submit for Judging"

- [ ] Repository is **public** and opens in a private browser window without login
- [ ] Demo video link is public, 30 seconds or less, with English subtitles if needed
- [ ] AI-generated clips in the video have a visible watermark; no NASA logo; nobody under 18
- [ ] All team members confirmed at the Uberlandia Local Event
- [ ] All form fields filled in English
- [ ] "Terms and Conditions" and "Confirm All Work is Original" checked
- [ ] Clicked **Submit for Judging** and saw the confirmation banner (resubmitting is allowed until the deadline)
