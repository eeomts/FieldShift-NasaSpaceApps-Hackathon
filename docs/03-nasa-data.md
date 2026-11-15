# NASA Data

Which NASA datasets and services AgroAI uses, at what resolution, and where each one shows up for the farmer.

Last updated: 2026-11-15

## Summary

| Dataset | What it gives the farmer | Where in the app | Status |
|---|---|---|---|
| NASA POWER | 30 years of local climate: rain, temperature, frost, heat, heavy rain, dry spells, and the inputs for evapotranspiration | Dashboard, rotation engine, chat | Working |
| SRTM 30 m | Terrain slope of the field | Rotation engine (erosion score), chat | Working |

**Status:** `Working` = used by the app today. Besides NASA data, the app uses **SoilGrids** (ISRIC) for soil properties and **Open-Meteo** for the 7-day forecast, because NASA does not publish forecasts.

**Not part of this version:** soil moisture (SMAP L4), NDVI (MODIS, VIIRS, HLS) and satellite rain (GPM IMERG). The rotation analysis does not use them: water comes from NASA POWER rain and climate, and the months with a crop in the field come from the calendar the farmer gives. They are on the [roadmap](05-limitations-roadmap.md).

## NASA POWER

- **Service:** POWER API, daily point endpoint (`power.larc.nasa.gov/api/temporal/daily/point`) and the climatology endpoint, `AG` community.
- **Variables:** `T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, `RH2M`, `ALLSKY_SFC_SW_DWN`, `WS2M`.
- **Resolution:** grid cell of about 0.5 deg (~50 km); monthly normals for 1991-2020.
- **How we use it:**
  - Monthly rain and temperature normals of the farm's location.
  - Frost risk, heat stress, heavy-rain days and dry spells, from daily data.
  - Reference evapotranspiration (ET0), **computed by AgroAI with the FAO-56 Penman-Monteith method** from the POWER variables. Crop water demand is then `ETc = Kc x ET0`, month by month.
  - Growing degree days, to check if a crop can finish its cycle in the available window.
- **Safety check:** if POWER changes the units of a variable, the app stops instead of computing with the wrong unit. Missing values (`-999`) are treated as missing, never as zero.

## SRTM

- **Product:** SRTM 30 m elevation, read through the OpenTopoData `srtm30m` service.
- **How we use it:** a 3 x 3 grid of elevations around the farm gives the slope (Horn method), classified into Embrapa relief classes, from flat to mountainous. Slope weighs the **erosion** score of each rotation: bare soil in the rainy months on a steep field scores worse.
- **Fallback:** if SRTM fails, the engine uses the farmer's own answer about the terrain and says so.

## How the app reads NASA data

- **Live, per farm:** the back-end calls the NASA POWER API for the farm's coordinates and SRTM through OpenTopoData. No whole files are downloaded.
- **Independent parts:** if one source fails, the others still show, and the missing part is listed with a reason. The app never fills the gap with an invented value.
- **Cache:** results are cached so the same farm does not hit the services twice.

## Sources

- NASA POWER: https://power.larc.nasa.gov
- SRTM: https://www.earthdata.nasa.gov/data/instruments/srtm
- SoilGrids (ISRIC): https://soilgrids.org
- Open-Meteo: https://open-meteo.com
- FAO-56 (ET0 method): https://www.fao.org/4/x0490e/x0490e00.htm
