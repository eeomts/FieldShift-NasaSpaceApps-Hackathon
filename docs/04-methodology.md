# Methodology

How AgroAI compares crop rotations, where every number comes from, and how uncertainty is shown.

Last updated: 2026-11-15

## Principles

1. **The tool supports, it does not decide.** The final word belongs to the farmer and the local agronomist.
2. **Every number has a source.** Each score breaks down to the data behind it (NASA dataset, crop catalog, or the farmer's answer).
3. **AI never computes or invents a number.** All scores come from transparent rules and formulas in code. The language model only reads free text and explains results in plain words.
4. **Missing data is shown, not filled.** When a source fails or the farmer answers "I don't know", the app records a gap and lowers confidence.

## Three calculations

| # | What | Technique |
|---|---|---|
| 1 | Farmer **profile** (how much the farmer knows about the soil) | Simple rules |
| 2 | **Soil portrait** (drainage, texture, organic matter, compaction, erosion) | Evidence fusion, weighted by source |
| 3 | **Rotation comparison** | Feasibility filter + multi-criteria scoring, weighted by the farmer's priorities |

## 1. Profile

- **C:** has a lab soil test in hand with at least 2 values.
- **B:** answered soil texture, or at least 5 of the 8 field-observation questions.
- **A:** everyone else.

The profile only changes how much detail the screens show. It does not change the scores.

## 2. Soil portrait (evidence fusion)

Each soil attribute receives evidence from several sources, each with a confidence weight:

| Source | Weight |
|---|---|
| Lab soil test | 0.9 |
| Guided field test | 0.7 |
| Farmer's observation (questionnaire) | 0.5 |
| SoilGrids (global model, 250 m) | 0.4 |
| "I don't know" | 0 (records a gap) |

When sources disagree, the app says so. Example: *"The global map suggests moderate drainage, but you saw water pooling. On your field, what you see counts."*

## 3. Rotation comparison

```
current rotation + candidates -> feasibility filter -> 6 criteria scored 0-1 -> farmer's priority weights -> current + 2 best
```

### a) Candidates

The current rotation is always included as the baseline. Candidates come from three rules over the crop catalog:

1. **Fill the bare window:** put a cover crop or a cash crop in the months when the field is empty.
2. **Swap for a drought-tolerant crop.**
3. **Add a legume:** fixes nitrogen and breaks pest cycles.

### b) Feasibility filter

A candidate is **eliminated** (with the reason shown) when:

- a cash crop cannot complete its cycle in the window: the 2001-2020 median of growing degree days is below 90 % of the crop's minimum (NASA POWER). Between 90 % and 100 %, and in cold years (1 in 10), it only warns;
- cold below the crop's own critical temperature hits its sensitive phase in more than 30 % of the years (NASA POWER daily minimum temperature);
- the farmer excluded the crop or lacks the required equipment;
- the crop needs flooded (irrigated) rice conditions the farm does not have;
- a **new** suggestion gets rain for less than half of its water demand and the farm has no irrigation.

A cover crop is only suggested inside its own sowing window. In the US, a cash crop is only suggested in a month of its usual planting window (USDA Handbook 628, "most active" dates in the reference state).

**Heat only warns:** when the daily maximum passes the crop's limit for 3 days in a row in the middle third of the cycle in more than 30 % of the years.

**Water never eliminates the current rotation, it only warns:** if crop demand (`ETc = Kc x ET0`) is above the rain of the period, the app flags it, and says whether irrigation covers part of the area.

### c) Six criteria, each from 0 to 1

| Criterion | How it is scored (simplified) | Main data |
|---|---|---|
| Save water | Crop water demand vs. rain of the period | NASA POWER (rain, ET0), crop Kc |
| Improve the soil | Months with cover (40 %) + biomass (30 %) + nitrogen fixation (30 %) | Crop catalog |
| Prevent erosion | Share of heavy-rain days that fall in months with a crop in the field, weighted by the slope (RUSLE slope factor) and the soil erodibility (USLE K) | NASA POWER, SRTM, SoilGrids |
| Fewer pests | Share of crop changes that switch botanical family (the rotation is a cycle: the last crop returns to the first) | Crop catalog |
| Extra income | Number of cash crops (1 -> 0.5, 2 -> 0.8, 3+ -> 1.0); cover crops do not count | Crop catalog |
| Animal feed | Forage value of the crops | Crop catalog |

### d) The farmer's priorities

The farmer picks up to 3 priorities. Weights: 1st = 0.5, 2nd = 0.3, 3rd = 0.2, rescaled so that each criterion not chosen still keeps 0.05 and does not disappear.

### e) Explanation of each strategy

For each strategy, the app shows what the challenge asks for:

- **Why it was suggested:** the criteria where it beats the current rotation by at least 0.1 (up to 3 sentences).
- **Evidence:** each score with the data behind it.
- **Benefits and risks:** warnings from the filter (water, thermal limit, cold years, heat).
- **Confidence:** the lowest confidence among the crops in the rotation.
- **Gaps:** what is missing and needs local review.

## Why not machine learning

There is no dataset of real rotation outcomes to train a model, and a model would be a black box. Rules and formulas are explainable to the farmer, and every score can be traced back to its source.

## Parameter status

Thresholds and weights live in one file (`agroai/api/app/services/motor/parametros.py`). Values marked as *proposal* in that file are initial values to be validated by an agronomist.

## Sources

- FAO-56, Crop evapotranspiration (ET0 and Kc): https://www.fao.org/4/x0490e/x0490e00.htm
- SoilGrids (ISRIC): https://soilgrids.org
- Embrapa relief classes (slope): Embrapa, *Sistema Brasileiro de Classificação de Solos* (in Portuguese)
- Crop parameters and their sources: `data/catalogo/culturas.csv`, `data/catalogo/evidencias/` (Brazil) and `data/catalogo/eua/` (US); evidence notes are in Portuguese
