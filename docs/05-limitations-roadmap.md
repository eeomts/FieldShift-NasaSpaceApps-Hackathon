# Limitations and Roadmap

What works today, what is partial, and what comes next. Stated honestly so the results can be judged fairly.

Last updated: 2026-11-15

## Status

| Part | Status |
|---|---|
| Sign-in and questionnaire (PT/EN) | Working |
| Climate from NASA POWER (normals, frost, heat, heavy rain, dry spells, ET0) | Working |
| Satellite data: SMAP soil moisture, MODIS/VIIRS NDVI, GPM IMERG rain | Not in this version: the analysis does not use them |
| Slope from SRTM | Working |
| Soil portrait (SoilGrids + farmer's observations) | Working |
| Rotation comparison: current + 2 alternatives, 6 criteria | Working (v1) |
| Chat assistant with knowledge base | Working (cites NASA POWER; slope from SRTM appears through the rotation comparison) |
| Official Brazilian planting windows (ZARC) | Partial: data prepared for 3 states, not yet read by the engine |
| US usual planting dates (USDA Handbook 628) | Working: the engine applies them to US cash crops |
| Market and income data (IBGE PAM, USDA NASS) | Partial: data prepared, not yet read by the engine |

## Known limitations

- **Parameters to validate.** Some thresholds and weights in the engine are initial proposals, marked in the code, and need review by an agronomist.
- **Resolution.** NASA POWER is about 50 km: it describes the region, not the single field, and a local summer storm may not show in full. SRTM (30 m) and SoilGrids (250 m) are closer to field scale. The farmer's own observations carry more weight than global models for the soil.
- **No outcome data.** There is no dataset of real rotation results to calibrate the scores. The comparison is a structured, explainable estimate, not a yield prediction.
- **No forecasts and no "what if" runs in the chat.** The chat explains the current comparison and the climate history; it does not re-run the engine with changed inputs.
- **Crop coverage.** 17 crops in Brazil and 18 in the US. Crops outside the catalog are not scored.

## Roadmap

1. Engine v2: official Brazilian planting windows (ZARC) and local market data in the "extra income" score.
2. "What if" scenarios: re-run the engine with less rain, more heat or irrigation, as a sensitivity test, not a forecast.
3. Satellite data (SMAP soil moisture, MODIS/VIIRS NDVI, GPM IMERG rain) in the analysis and in the chat.
4. More crops and regional crop arrangements.
5. Validation with agronomists and extension services in each region.
6. Field-level layers: erosion-risk zones and water-stress hotspots on the map.
