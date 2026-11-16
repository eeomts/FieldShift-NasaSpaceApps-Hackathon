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
| OpenStreetMap map tiles | Base map in the questionnaire | © OpenStreetMap contributors, ODbL; tile usage policy |
| OpenTopoData | Access to SRTM 30 m elevation | Public API |
| MAPA, ZARC risk tables 2025/2026 and 2026/2027 (Brazil) | Official planting windows (prepared, see roadmap) | Brazilian open government data |
| IBGE, municipalities API and mesh v3 | Brazilian municipalities | Brazilian open government data |
| IBGE SIDRA, Municipal Agricultural Production (PAM), table 5457 | Crop production per municipality (prepared) | Brazilian open government data |
| USDA NASS, Usual Planting and Harvesting Dates (Handbook 628, 2010) | US cash-crop planting windows, transcribed into the US crop catalog and applied by the engine | Public domain (US government) |
| USDA NASS Quick Stats | US county crop production, 2016-2025 (prepared) | Public domain (US government) |
| USDA NASS Cropland Data Layer (CropScape), 2020-2024 | Checking the rotation of the US demo farms | Public domain (US government) |
| US Census Bureau TIGERweb | US counties | Public domain (US government) |
| FAO-56 | ET0 and crop coefficient (Kc) method | FAO publication |
| Brazil crop parameters: Embrapa, FAO, IAPAR/IDR-Parana, ZARC, and the literature cited per crop | Cycle, temperature, water, Kc, frost of 17 crops | See `data/catalogo/evidencias/` (notes in Portuguese) |
| US crop parameters: USDA (NRCS, ARS), university extension services, FAO | Same parameters for 18 crops | See `data/catalogo/eua/evidencias/` (notes in Portuguese) |

The team's full download log (file, URL, date, version, license) is in [`data/FONTES.md`](../data/FONTES.md) (in Portuguese; the table above is its English summary).

## Images

Soil reference photos in the questionnaire come from **Wikimedia Commons**, downloaded on 2026-11-14. The six color photos (`cor_*`) were cropped so the soil fills the frame; colors were not changed. The six texture photos (`jeito_*`) were only resized.

| File | Author | Source | License |
|---|---|---|---|
| `cor_escura.jpg` | Adam Jones | https://commons.wikimedia.org/wiki/File:Black_Earth_-_Prokhorovka_-_Russia.JPG | CC BY-SA 3.0 (cropped) |
| `cor_marrom.jpg` | Zmu'az4Z | https://commons.wikimedia.org/wiki/File:Texture_of_a_fertile_soil.jpg | CC BY 4.0 (cropped) |
| `cor_vermelha.jpg` | David Jackmanson | https://commons.wikimedia.org/wiki/File:Rich,_red_soil_in_parts_of_the_island_-_Russell_Island,_Moreton_Bay,_Queensland,_2012.jpg | CC BY 2.0 (cropped) |
| `cor_amarela.jpg` | Ray Isbell, CSIRO | https://commons.wikimedia.org/wiki/File:CSIRO_ScienceImage_4302_Yellow_Kandosol_soil_profile_in_the_Bamaga_Reserve_Cape_York_Peninsula_north_Queensland.jpg | CC BY 3.0 (cropped) |
| `cor_cinza.jpg` | Jonty68 (en.wikipedia) | https://commons.wikimedia.org/wiki/File:Gley.JPG | Public domain (cropped) |
| `cor_clara.jpg` | Unknown author ("own work") | https://commons.wikimedia.org/wiki/File:Podzol_soil.JPG | Public domain (cropped) |
| `jeito_solta.jpg` | freestocks.org | https://commons.wikimedia.org/wiki/File:Sea_beach_sand_in_a_hand_closeup_(42621473960).jpg | CC0 |
| `jeito_fofa.jpg` | Soil Science | https://commons.wikimedia.org/wiki/File:Soil_material_containing_Sand,_silt,_clay.jpg | CC BY 2.0 |
| `jeito_gruda.jpg` | Cmoffroad | https://commons.wikimedia.org/wiki/File:Red-clay-sticky-plastic-when-wet.jpg | CC0 |
| `jeito_torroes.jpg` | Mclund | https://commons.wikimedia.org/wiki/File:SoilClod.jpg | CC BY 4.0 |
| `jeito_racha.jpg` | Wilfredor | https://commons.wikimedia.org/wiki/File:Polygonal_cracks_in_drought-dried_soil_near_La_Guardia,_Margarita_Island,_Venezuela.jpg | CC0 |
| `jeito_pedras.jpg` | Alan Murray-Rust | https://commons.wikimedia.org/wiki/File:Stony_soil_-_geograph.org.uk_-_6596682.jpg | CC BY-SA 2.0 |

## Fonts

| Font | Source | License |
|---|---|---|
| Bricolage Grotesque | Google Fonts | SIL Open Font License 1.1 |
| DM Sans | Google Fonts | SIL Open Font License 1.1 |

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
