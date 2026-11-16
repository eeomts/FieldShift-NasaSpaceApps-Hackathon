# Overview

The problem AgroAI addresses, who it is for, and what it does.

Last updated: 2026-11-15

## The problem

Small and mid-size farmers face shifting temperatures, irregular rain, water shortages and declining soil health. Choosing **what to plant and when** gets harder every season. A crop that improves the soil in one place may use too much water, fall outside the growing season, or carry frost risk somewhere else.

NASA has decades of free data about every field on Earth: rain, temperature, soil moisture, vegetation, terrain. But for most farmers this data is out of reach: it is spread across many portals, in technical formats, in English, and needs expertise to read.

## Who it is for

- **Small and mid-size farmers** in Brazil and the United States, with little time and limited technical background.
- **Local agronomists and extension technicians**, who can use the same screens with more detail.

## The solution: AgroAI

A mobile-first website, in **Portuguese and English**, where the farmer:

1. **Answers a short questionnaire** about the farm: location, what is planted and when, what the farmer knows about the soil, available equipment, and the farmer's own priorities (save water, improve the soil, prevent erosion, fewer pests, extra income, animal feed).
2. **Sees a dashboard** with the farm's climate history (NASA POWER), recent satellite readings (SMAP soil moisture, MODIS NDVI, GPM IMERG rain), terrain slope (SRTM), a soil portrait (SoilGrids + the farmer's observations) and the weather forecast.
3. **Compares three rotation strategies**, the current one plus the two best alternatives for the farmer's priorities. For each: why it was suggested, the evidence, benefits, risks, confidence and information gaps.
4. **Talks to the AgroAI assistant**, a chat that knows the farm and answers "what if" questions in plain language, always citing the source of each number.

> AgroAI **supports, it does not decide**. The final word belongs to the farmer and the local expert. Every number has a source, and the AI never computes or invents a number.

## How it answers the Field Shift challenge

| The challenge asks for | AgroAI |
|---|---|
| Use NASA Earth observations | NASA POWER (climate) and SRTM (slope) (see [NASA Data](03-nasa-data.md)) |
| Combine with local soil, crop characteristics and farmer priorities | SoilGrids + farmer's observations; catalog of 17 crops (Brazil) and 18 crops (US) with sourced parameters; the farmer's own priorities weight the comparison |
| Compare at least 3 rotation strategies, including the current one | Current rotation + 2 best alternatives |
| Explain why, evidence, benefits, gaps and risks | Shown for each strategy (see [Methodology](04-methodology.md)) |
| Highlight bare-field periods and vulnerable seasons | Bare-window detection, cold and heat in each crop's sensitive phase, water deficit, heavy-rain months |
| Be easy for farmers with limited technical experience | Plain language, mobile first, PT/EN, chat assistant |
| Support, not replace, local expertise | Stated on every comparison; confidence and gaps shown |

## Why it matters

- It turns NASA data into decisions a farmer can act on this season: what to put in the empty months, which crop handles a dry year better, where erosion risk is high.
- Every recommendation is explainable, so the farmer and the agronomist can check it instead of trusting a black box.
- Healthier rotations mean more soil cover, less erosion, less water stress and more resilient income.
