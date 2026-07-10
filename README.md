# app-multiagent-research-multivocal

Multi-agent application to automate the research pipeline of the multivocal review
(search, screening, and cataloguing).

The pipeline is run from the command line, one **origin** and one **step** at a time.

## Requirements

- Python 3.11+ managed by [uv](https://docs.astral.sh/uv/).
- Create the environment / install dependencies: `uv sync`.
- A [Firecrawl](https://www.firecrawl.dev/) API key (free subscription works fine for few results).
- A [Scopus](https://dev.elsevier.com/) API key (free tier API works fine for few results).
- An LLM API key from an OpenAI-compatible provider ([OpenRouter](https://openrouter.ai/) or [Azure AI Foundry](https://ai.azure.com/)).

This project uses **uv** for everything (dependencies, virtual environment, running).
Use `uv add <pkg>` to add a dependency and `uv run <cmd>` to run code.

## Configuration

Copy `.env.example` to `.env` at the repository root and fill in the values (never commit the
real `.env`):

| Variable                 | Description                                                              |
|--------------------------|-------------------------------------------------------------------------|
| `FIRECRAWL_API_KEY`      | Firecrawl API key; grey-literature search and scraping (steps 1, 3).    |
| `SCOPUS_API_KEY`         | Scopus Search API key; academic search (step 1).                        |
| `MODEL_EXPERIMENT`       | Subfolder name isolating one model's screening outputs (steps 2-4).     |
| `LLM_BASE_URL`           | OpenAI-compatible endpoint base URL; empty defaults to OpenRouter.      |
| `LLM_API_KEY`            | API key for the LLM endpoint.                                           |
| `LLM_MODEL`              | Model / deployment name; empty uses the endpoint's default.            |
| `LLM_API`                | `chat` (Chat Completions, default) or `responses` (Responses API).      |
| `LLM_TEMPERATURE`        | Sampling temperature (default `0.2`); leave empty to omit it.           |
| `OPENROUTER_API_KEY`     | Legacy fallback, used only when the `LLM_*` variables are empty.        |
| `REVIEW_DRIVE_FOLDER_URL`| Shared Drive folder link; makes step-4 review file names clickable (step 5). |

## Protocol settings

The review protocol lives as JSON under `protocol-settings/`:

| File                             | Description                                                        |
|----------------------------------|-------------------------------------------------------------------|
| `1-research-question.json`       | Central research question and sub-questions (RQa–RQh).            |
| `2-search-string.json`           | PICOC search terms (population, intervention, outcome, context).  |
| `3-inclusion-criterias.json`     | Inclusion criteria (IC1–IC5).                                     |
| `4-exclusion_criterias.json`     | Exclusion criteria (EC1–EC5).                                     |
| `5-grey-quality-appraisal.json`  | Quality-appraisal dimensions for grey literature.                 |

Invariant execution rules (Scopus field scope, year window, subject area, document type,
language, query splitting for grey literature) live in the code, not in these files.

## Usage

```
uv run python main.py --origin <scopus|google|github|hf> --step <1|2|3|4>
```

Both parameters are **required** for steps 1-4. Steps 5-7 (review) take no `--origin`.

## Origins

| Value    | Source                                                                 |
|----------|------------------------------------------------------------------------|
| `scopus` | Scopus (academic literature), via the Scopus Search API                |
| `google` | Google general web (grey literature), via Firecrawl                     |
| `github` | GitHub, via Firecrawl with `site:github.com`                            |
| `hf`     | Hugging Face Papers, via Firecrawl with `site:huggingface.co/papers`    |

The `hf` origin replaces Papers With Code, which was discontinued during the study and
now redirects to Hugging Face Papers. In the manuscript this substitution is noted in the
text; the PRISMA flow and Table 1 keep their original labels.

## Steps

| Step | Meaning                                               |
|------|-------------------------------------------------------|
| `1`  | Initial complete search                               |
| `2`  | Title screening                                       |
| `3`  | Abstract & keywords screening                         |
| `4`  | Full-text screening                                   |
| `5`  | Export blind human-review spreadsheets (all origins)  |
| `6`  | Generate blind tie-break spreadsheets (all origins)   |
| `7`  | Compute screening metrics from the human reviews      |

## Review (step 5)

```
uv run python main.py --step 5
```

Exports blind human-review spreadsheets (`.xlsx`), one per screening step, covering all origins.
The reviewer fills the last column (an empty dropdown) without seeing the LLM's decision.

| File                         | Description                                    |
|------------------------------|------------------------------------------------|
| `step-2-review.xlsx`         | Title-screening review.                        |
| `step-3-review.xlsx`         | Abstract-screening review.                     |
| `step-4-review.xlsx`         | Full-text-screening review.                    |
| `step-4-answers-review.xlsx` | Research answers and IC2/IC3 audit.            |

## Tie-break (step 6)

```
uv run python main.py --step 6
```

Reads the filled review sheets and writes blind tie-break sheets to `.../tiebreak/`, holding
only the rows where reviewer 1 disagrees with the LLM, for a second reviewer to resolve.

## Metrics (step 7)

```
uv run python main.py --step 7
```

Computes the LLM screening reliability from the filled sheets (all must be complete), writing
`.../metrics/metrics.json` plus a console summary. The gold standard is reviewer 1, with reviewer
2 breaking ties; the positive class is `include`. Reported per origin and pooled:

| Metric                            | Description                                          |
|-----------------------------------|------------------------------------------------------|
| Precision / Recall / F1           | LLM vs gold.                                        |
| Accuracy                          | Overall correctness of the LLM decisions.           |
| Confusion matrix                  | TP / FP / FN / TN counts.                           |
| Agreement                         | How often the LLM and reviewer 1 decided the same.  |
| Conflicts                         | Rows where the LLM and reviewer 1 disagree.         |
| Adjudication                      | How reviewer 2 resolved those conflicts.            |
| Validation rate                   | `step-4-answers`: share confirmed after adjudication. |
