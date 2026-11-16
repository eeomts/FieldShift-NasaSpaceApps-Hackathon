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

**Rule enforced in the code and in the prompt:** every number shown to the farmer comes from a NASA dataset, the crop catalog, or a formula in code. The AI only explains them. When the AI is unavailable, the questionnaire falls back to the crop list and the scores are unchanged.

## 2. AI-assisted code development

- **The code of AgroAI was developed with AI assistance.** The team used **Claude Code (Anthropic)** to help write and review the code, tests, data-preparation scripts and documentation, including this documentation.
- The team defined the idea, the product rules, the data choices and the methodology. AI was used to speed up implementation, not to come up with the solution.
- All AI-assisted code was reviewed and tested by the team (automated tests in `agroai/api/tests`).

## 3. AI-edited demo video

- **The demo video was edited with AI tools:** Claude Opus 5.5 (Anthropic).
- The video carries a **visible watermark** stating that AI was used in its production.
- No AI-generated or AI-edited content uses NASA logos, flags or mission identifiers.
- No images or videos show people under 18.

## Where this is disclosed

As the rules ask for both descriptive text and metadata, this statement appears in:

- this file and the root `README.md` (descriptive text);
- the project form, field "Use of Super Intelligence (SI)";
- the watermark on the demo video.

## Sources

- NASA Space Apps, Project Submission Guide: "Use of Super Intelligence (SI)".
