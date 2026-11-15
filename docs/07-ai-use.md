# Use of AI (Super Intelligence)

Where and how AI tools were used in AgroAI, as required by the NASA Space Apps rules.

Last updated: 2026-11-15

## 1. AI inside the product

AgroAI uses **Google Gemini** (`google-genai` SDK) for three tasks:

| Task | What the AI does | What the AI does NOT do |
|---|---|---|
| Questionnaire | Reads the farmer's free-text answers (e.g. crop names written their own way) and maps them to the crop catalog | Decide or score anything |
| Chat assistant | Answers the farmer's questions in plain language, using the farm's data and the knowledge base, and cites the source | Compute, estimate or invent numbers |
| Knowledge base search (RAG) | Creates embeddings to find the right explanation texts | - |

**How numbers stay out of the AI's hands:** every score is computed in code, outside the model, from a NASA dataset, the crop catalog or a formula. The model only receives numbers through the results of the tools it calls, and the prompt forbids it from producing numbers of its own. The answer text is not checked number by number, so the chat also shows the sources returned by the tools. When the AI is unavailable, the questionnaire falls back to the crop list and the scores are unchanged.

## 2. AI-assisted code development

- **The code of AgroAI was developed with AI assistance.** The team used **Claude Code (Anthropic)** to help write and review the code, tests, data-preparation scripts and documentation, including this documentation.
- **Data:** the team also used Claude Code to research and compile the crop-parameter catalog (`data/catalogo/`) from primary sources (Embrapa, FAO, USDA, university extension services). Every value keeps its cited source in the evidence files.
- The team defined the idea, the product rules, the data choices and the methodology. AI was used to speed up implementation, not to come up with the solution.
- All AI-assisted code was reviewed and tested by the team (automated tests in `agroai/api/tests`).

## 3. AI-generated clips in the demo video

- **The demo video uses AI-generated clips**, made and edited with [TODO: name the tool(s)].
- **Every AI-generated clip carries a visible watermark** stating that it was generated with AI.
- AI-generated voice or music, if any, is stated in the video description.
- No AI-generated or AI-edited content uses NASA logos, flags or mission identifiers.
- No images or videos show people under 18.

## Where this is disclosed

As the rules ask for both descriptive text and metadata, this statement appears in:

- this file and the root `README.md` (descriptive text, for code, data and media);
- the project form, field "Use of Super Intelligence (SI)";
- the watermark on each AI-generated clip of the demo video;
- the video description on the hosting site (metadata): "Contains AI-generated footage".

## Sources

- NASA Space Apps, Project Submission Guide: "Use of Super Intelligence (SI)".
