# Space Apps Project Submission

Text for each field of the NASA Space Apps project page, ready to copy and paste. All fields must be in English.

Last updated: 2026-11-15 | Deadline: Sunday, 2026-11-15, 11:59 p.m. (local time of the Uberlandia Local Event)

---

## Project Name

AgroAI

## High-Level Project Summary

AgroAI is a mobile-first decision-support website, in English and Portuguese, that helps small and mid-size farmers in Brazil and the United States choose healthier crop rotations. The farmer answers a short questionnaire about the farm, the current crops, what they know about the soil and their own priorities (save water, improve the soil, prevent erosion, fewer pests, extra income, animal feed). AgroAI then combines NASA Earth observations (NASA POWER climate and SRTM slope) with soil data and a sourced crop catalog to compare the current rotation with the two best alternatives. For each strategy it explains why it was suggested, the evidence, benefits, risks, confidence and information gaps, exactly what the Field Shift challenge asks for. A chat assistant explains the results and the farm's climate in plain language and cites the source of every number. AgroAI supports, it does not decide: all scores come from transparent rules, the AI never computes or invents a number, and the final word belongs to the farmer and the local expert.

## Link to Project Demo

https://www.youtube.com/watch?v=Do6FTY6CYfc

## Link to Final Project

https://github.com/eeomts/FieldShift-NasaSpaceApps-Hackathon

The repository README links to the live demo, which needs no password (sign in with any name, the demo farm is pre-filled): https://demo-agroai.mateusmoreira.dev

## Detailed Project Description

**What it does.** AgroAI turns decades of free NASA data into a crop-rotation comparison a farmer can act on this season. It shows the months when the field is bare, the seasons when the current crops are more vulnerable (frost in flowering, water deficit, heavy rain on bare soil), and rotation options that fill those gaps.

**How it works.**
1. *Questionnaire:* the farmer marks the farm on a map and answers about crops and planting months, soil observations (with reference photos), equipment, irrigation and up to 3 priorities. "I don't know" is always accepted.
2. *Data collection:* from the location, the back-end reads NASA POWER (daily data and 1991-2020 normals), SRTM slope, SoilGrids soil properties and a 7-day forecast.
3. *Soil portrait:* evidence fusion of lab results, field tests, the farmer's observations and SoilGrids, each with a confidence weight. When sources disagree, the app says so and trusts what the farmer sees.
4. *Rotation engine:* generates candidates (fill the bare window, swap for a drought-tolerant crop, add a legume), removes infeasible ones (growing degree days, frost in flowering, equipment, excluded crops, and, in the US, cash crops outside their usual planting window from USDA Handbook 628) and scores each on 6 criteria from 0 to 1: water, soil, erosion, pests, income and animal feed. Water demand uses FAO-56 (ET0 from NASA POWER, ETc = Kc x ET0); erosion uses rainfall, SRTM slope and soil erodibility. The farmer's priorities weight the final score.
5. *Results:* the current rotation and the 2 best alternatives, each with why, evidence, risks, confidence and gaps. The chat assistant explains them in plain language, with the source and period of each number.

**Benefits.** Free NASA data becomes plain-language guidance; every recommendation is explainable and traceable to its source; the farmer's own knowledge counts; and it is built for the phone, in two languages.

**What we hope to achieve.** Help farmers adopt rotations that keep the soil covered, reduce erosion and water stress and add income, while giving agronomists a transparent tool they can check and adapt. Next steps: official Brazilian planting windows (ZARC) in the engine, local market data, satellite data (SMAP, NDVI, GPM IMERG) in the analysis and the chat, and validation with extension services.

**Tools and languages.** Python (FastAPI, SQLAlchemy, Alembic, Pydantic, pytest), PostgreSQL with pgvector, TypeScript (React, Vite, Tailwind CSS, Leaflet), Docker, Google Gemini for language tasks only.

Full documentation: `docs/README.md` in the repository.

## Use of Super Intelligence (SI)

Yes. (1) The code was developed with AI assistance: the team used Claude Code (Anthropic) to help write and review code, tests, data scripts and documentation. The idea, product rules, data choices and methodology are the team's, and all code was reviewed and tested by the team. (2) The team also used Claude Code to research and compile the crop-parameter catalog from primary sources (Embrapa, FAO, USDA, extension services); every value keeps its cited source in `data/catalogo/`. (3) The demo video was generated with Claude Opus 5.5 (Anthropic): illustrations, animation, captions and the code of the background music. The narrator voice was synthesized with Chatterbox TTS (Resemble AI), cloned from team member Guilherme Melo's own voice with his consent; the voice of the fictional farmer "Dona Marta" is Microsoft Ava neural TTS. A visible "AI-generated (SI)" watermark is on every frame, and the MP4 metadata states it too. Numbers on screen are illustrative. (4) In the product, Google Gemini reads the farmer's free-text answers, powers the chat assistant and creates embeddings for the knowledge-base search. It never computes or invents numbers: every number comes from NASA data, the crop catalog or a formula in code, and the prompt forbids the model from producing numbers on its own. No AI-generated content uses NASA branding. Details: `docs/07-ai-use.md`.

## NASA Data

- **NASA POWER** (daily point API and climatology, AG community: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M, ALLSKY_SFC_SW_DWN, WS2M): 1991-2020 rain and temperature normals, frost, heat, heavy-rain days, dry spells, growing degree days, and reference evapotranspiration (FAO-56, computed by AgroAI).
- **SRTM 30 m**: field slope (Horn method), used in the erosion score.

Not part of this version: SMAP soil moisture, MODIS/VIIRS NDVI and GPM IMERG rainfall. They are on the roadmap.

Details: `docs/03-nasa-data.md`.

## Space Agency Partner Data and Other References

We did not use data from the Space Agency Partners. Other references:

- **Data:** SoilGrids 2.0 (ISRIC, CC BY 4.0); Open-Meteo forecast (CC BY 4.0); OpenStreetMap Nominatim (ODbL); OpenTopoData (SRTM access); MAPA ZARC risk tables (Brazil); IBGE municipalities and SIDRA PAM table 5457; USDA NASS Quick Stats, Usual Planting and Harvesting Dates (Handbook 628) and Cropland Data Layer; US Census TIGERweb; FAO-56; crop parameters from Embrapa, FAO, IAPAR/IDR-Parana, USDA NRCS/ARS and university extension services.
- **Map:** OpenStreetMap map tiles (© OpenStreetMap contributors, ODbL).
- **Fonts:** Bricolage Grotesque and DM Sans (Google Fonts, SIL Open Font License 1.1).
- **Images:** soil reference photos from Wikimedia Commons (CC0, public domain, CC BY, CC BY-SA), with authors and licenses listed in `docs/06-references.md`.
- **Code libraries:** FastAPI, Uvicorn, SQLAlchemy, psycopg, Alembic, Pydantic, argon2-cffi, PyJWT, httpx, Shapely, pgvector, google-genai, pytest, React, React Router, Leaflet, React Leaflet, Vite, TypeScript, Tailwind CSS, PostgreSQL, Docker, Caddy.
- **AI services:** Google Gemini, Claude Code.

Details: `docs/06-references.md`.

---

## Checklist before "Submit for Judging"

Every item comes from the official [Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/).

**Eligibility**
- [ ] All team members are confirmed participants at the same Local Event (Uberlandia); nobody is waitlisted
- [ ] Clicked **Submit for Judging** before Sunday, 2026-11-15, 11:59 p.m. local time; anything saved after that is not judged

**Form fields (all required, all in English)**
- [ ] Project Name
- [ ] High-Level Project Summary
- [ ] Link to Project Demo (no `[TODO]` left)
- [ ] Link to Final Project
- [ ] Detailed Project Description (what it does, how it works, benefits, goals, tools and languages)
- [ ] Use of Super Intelligence (SI), with the video tool names filled in
- [ ] NASA Data (at least one NASA dataset: required for a Global Award)
- [ ] Space Agency Partner Data and Other References (all data, code, text, images, fonts, even if open source)

**Links**
- [ ] Every link is public: no password, permission, login or registration
- [ ] Tested in a private browser window: GitHub repository (https://github.com/eeomts/FieldShift-NasaSpaceApps-Hackathon), demo video, live demo (https://demo-agroai.mateusmoreira.dev)
- [ ] Linked materials are in English (the repository README and `docs/`)
- [ ] Optional but recommended for the new website: FortiGuard Web Filter Classification request, Company Name "N/A"

**Demo (one format only)**
- [ ] Video of **30 seconds or less**, or a slide deck of **7 slides or less** (title and intro included); over the limit means no Global Judging
- [ ] Hosted outside the Space Apps site (YouTube, Google Drive, GitHub...), public link
- [ ] Video: narration in English, or English subtitles; deck: all in English
- [ ] Deck only: team name, team member names and the challenge on the slides
- [ ] Shows the project, the user experience and how NASA data makes it possible

**Super Intelligence and media rules**
- [ ] Every AI-generated image or video clip has a **visible watermark**
- [ ] AI-generated audio (voice, music) acknowledged in the description text and metadata
- [ ] AI-assisted code and data acknowledged in the text (README, `docs/07-ai-use.md`, SI field)
- [ ] No AI-generated content uses or modifies NASA logos, flags or mission identifiers
- [ ] No images, video, audio or likeness of anyone under 18
- [ ] Copyrighted material (music, footage, photos) only with permission; licenses listed

**Final step**
- [ ] "Terms and Conditions" checked
- [ ] "Confirm All Work is Original" checked
- [ ] Confirmation banner seen after **Submit for Judging** (resubmitting is allowed until the deadline; only the last submission is judged)
