# AgroAI Documentation

Start here. AgroAI is a crop-rotation decision-support tool for small and mid-size farmers, built for the **NASA Space Apps Challenge 2026**, challenge **Field Shift: Adapting Farms with NASA Data**.

| # | Document | What you will find |
|---|---|---|
| 1 | [Overview](01-overview.md) | The problem, who it is for, the solution, how it answers the challenge |
| 2 | [How It Works](02-how-it-works.md) | The farmer's journey, architecture, tech stack |
| 3 | [NASA Data](03-nasa-data.md) | Each NASA dataset: product, version, resolution, how it is used |
| 4 | [Methodology](04-methodology.md) | How rotations are compared and where each number comes from |
| 5 | [Limitations and Roadmap](05-limitations-roadmap.md) | What works, what is partial, what comes next |
| 6 | [References](06-references.md) | Non-NASA data, libraries, images and licenses |
| 7 | [Use of AI](07-ai-use.md) | Where and how AI was used |
| 8 | [Run Locally](08-run-locally.md) | How to run the app |
| - | [Submission](submission/SUBMISSION.md) | The Space Apps project form, field by field |

## Judging criteria map

| Criterion | Where to look |
|---|---|
| **Impact** | [Overview](01-overview.md): the farmer's problem and why it matters |
| **Creativity** | [How It Works](02-how-it-works.md): an assistant that explains the results with the farm's own data and cites every source; explainable rotation comparison |
| **Validity** | [NASA Data](03-nasa-data.md), [Methodology](04-methodology.md), [Limitations](05-limitations-roadmap.md): every number has a source, gaps are shown |
| **Relevance** | [Overview](01-overview.md), section "How it answers the Field Shift challenge" |
| **Presentation** | The demo video and the app itself (live demo, no password: https://demo-agroai.mateusmoreira.dev) |

## Writing rules for these documents

- English, plain language, short.
- Every number has a source, listed in a **Sources** section or linked to the code.
- Status is honest: `Working`, `Partial` or `Planned`.
- The team's internal working notes (in Portuguese) are not part of this documentation.
- A few data files referenced as sources (the crop evidence files and the download log in `data/`) are the team's working records and are in Portuguese; their content is summarized in English in [References](06-references.md).
