# Tools and Data Sources

The NASA data, the data prepared by the team, and the other external data and services used by AgroAI, with their URLs.

Last updated: 2026-11-15

## 1. NASA data

| Tool | Used for | URL |
|---|---|---|
| NASA POWER, daily data | Daily climate: frost, heat, heavy rain, dry spells, ET0 | https://power.larc.nasa.gov/api/temporal/daily/point |
| NASA POWER, climatology | 1991-2020 climate normals | https://power.larc.nasa.gov/api/temporal/climatology/point |
| NASA POWER (website) | | https://power.larc.nasa.gov |
| SRTM 30 m | Field slope and erosion score | https://www.earthdata.nasa.gov/data/instruments/srtm |
| OpenTopoData (serves SRTM) | Elevation on a 3 x 3 grid | https://api.opentopodata.org/v1/srtm30m |
| SMAP L4 (SPL4SMGP) | Dashboard only: surface and root-zone soil moisture vs. past years | https://nsidc.org/data/spl4smgp |
| MODIS MOD13Q1 v061 | Dashboard only: NDVI over the last 12 months | https://lpdaac.usgs.gov/products/mod13q1v061/ |
| GPM IMERG Late, daily v07 | Dashboard only: rain over the last 30 days | https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDL_07/summary |
| NASA Earthdata (CMR + OPeNDAP, needs a token) | Finding and reading the SMAP, MODIS and IMERG pixel of the farm | https://cmr.earthdata.nasa.gov/search |

## 2. Data prepared by the team

| Tool | Used for | URL |
|---|---|---|
| MAPA, ZARC risk tables (Brazil) | Official planting windows | https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico |
| IBGE, municipalities | List of Brazilian municipalities | https://servicodados.ibge.gov.br/api/v1/localidades/municipios |
| IBGE, mesh v3 | Municipality boundaries | https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR |
| IBGE SIDRA, PAM table 5457 | Crop production per municipality | https://sidra.ibge.gov.br/tabela/5457 (API: https://apisidra.ibge.gov.br/values/t/5457) |
| USDA NASS, Handbook 628 | US planting windows | https://esmis.nal.usda.gov/publication/usual-planting-and-harvesting-dates-us-field-crops |
| USDA NASS Quick Stats | US county crop production | https://quickstats.nass.usda.gov/api |
| USDA CropScape (CDL) | Checking the rotation of the US demo farms | https://nassgeodata.gmu.edu/CropScape/ |
| US Census TIGERweb | US counties | https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1 |
| Wikimedia Commons | Soil photos in the questionnaire (author and license of each photo in [References](docs/06-references.md)) | https://commons.wikimedia.org |

## 3. Other external data and services

| Tool | Used for | URL |
|---|---|---|
| SoilGrids 2.0 (ISRIC) | Soil properties, 250 m | https://rest.isric.org/soilgrids/v2.0/properties/query (website: https://soilgrids.org) |
| Open-Meteo | 7-day weather forecast | https://api.open-meteo.com/v1/forecast (website: https://open-meteo.com) |
| Nominatim (OpenStreetMap) | Address search and reverse geocoding | https://nominatim.openstreetmap.org/search and https://nominatim.openstreetmap.org/reverse |
| OpenStreetMap map tiles | Base map in the questionnaire | https://tile.openstreetmap.org/{z}/{x}/{y}.png (license: https://www.openstreetmap.org/copyright) |
| FAO-56 | ET0 and crop coefficient (Kc) method | https://www.fao.org/4/x0490e/x0490e00.htm |

More details: [NASA Data](docs/03-nasa-data.md), [References](docs/06-references.md) and the team's download log in [`data/FONTES.md`](data/FONTES.md) (in Portuguese).
