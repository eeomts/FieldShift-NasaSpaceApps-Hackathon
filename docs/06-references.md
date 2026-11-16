# References

All data, services, libraries and media used in AgroAI, other than NASA data (listed in [NASA Data](03-nasa-data.md)).

Last updated: 2026-11-15

## Space Agency Partner data

AgroAI does not use data from the 2026 Space Agency Partners.

## Data and services

| Source | Used for | License / terms |
|---|---|---|
| SoilGrids 2.0 (ISRIC) | Soil texture, organic matter, pH and erodibility per point, 250 m | CC BY 4.0 |
| Open-Meteo | 7-day weather forecast | CC BY 4.0 (free non-commercial API) |
| OpenStreetMap Nominatim | Address search and reverse geocoding | ODbL; Nominatim usage policy |
| OpenTopoData | Access to SRTM 30 m elevation | Public API |
| MAPA, ZARC risk tables 2025/2026 and 2026/2027 (Brazil) | Official planting windows (prepared, see roadmap) | Brazilian open government data |
| IBGE, municipalities API and mesh v3 | Brazilian municipalities | Brazilian open government data |
| IBGE SIDRA, Municipal Agricultural Production (PAM), table 5457 | Crop production per municipality (prepared) | Brazilian open government data |
| USDA NASS, Usual Planting and Harvesting Dates (Handbook 628, 2010) | US planting windows, transcribed into the US crop catalog | Public domain (US government) |
| USDA NASS Quick Stats | US county crop production, 2016-2025 (prepared) | Public domain (US government) |
| USDA NASS Cropland Data Layer (CropScape), 2020-2024 | Checking the rotation of the US demo farms | Public domain (US government) |
| US Census Bureau TIGERweb | US counties | Public domain (US government) |
| FAO-56 | ET0 and crop coefficient (Kc) method | FAO publication |
| Brazil crop parameters: Embrapa, FAO, IAPAR/IDR-Parana, ZARC, and the literature cited per crop | Cycle, temperature, water, Kc, frost of 17 crops | See `data/catalogo/evidencias/` |
| US crop parameters: USDA (NRCS, ARS), university extension services, FAO | Same parameters for 18 crops | See `data/catalogo/eua/evidencias/` |

The full download log (file, URL, date, version, license) is in [`data/FONTES.md`](../data/FONTES.md).

## Images

Soil reference photos in the questionnaire come from **Wikimedia Commons** (CC0, public domain, CC BY and CC BY-SA). Authors, links, licenses and edits (cropping) are listed in [`agroai/web/public/fotos-solo/CREDITOS.md`](../agroai/web/public/fotos-solo/CREDITOS.md).

## Software libraries

| Area | Libraries |
|---|---|
| Back-end | FastAPI, Uvicorn, SQLAlchemy, psycopg, Alembic, Pydantic, pydantic-settings, email-validator, argon2-cffi, PyJWT, httpx, Shapely, pgvector, google-genai, pytest |
| Front-end | React, React DOM, React Router, Leaflet, React Leaflet, Vite, TypeScript, Tailwind CSS |
| Data scripts | Python standard library, requests |
| Infrastructure | PostgreSQL 17, pgvector, Docker, Caddy |

All libraries are open source under their own licenses.

## AI services

- Google Gemini (in the product) and Claude Code (development). See [Use of AI](07-ai-use.md).
