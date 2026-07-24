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

Invariant execution rules (Scopus field scope, year window, subject area, document type,
language, query splitting for grey literature) live in the code, not in these files.

## Usage

```
uv run python main.py --origin <scopus|google|github|hf> --step <1|2|3|4>
```

Both parameters are **required** for steps 1-4. Steps 5-8 (review) take no `--origin`.

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
| `6`  | Report the rows awaiting adjudication (`Review 2`)    |
| `7`  | Compute screening metrics from the human reviews      |
| `8`  | Reconcile the human review and report the residuals   |

## Review (step 5)

```
uv run python main.py --step 5
```

Exports blind human-review spreadsheets (`.xlsx`), one per screening step, covering all origins.

| File                         | Description                                                     |
|------------------------------|-----------------------------------------------------------------|
| `step-2-review.xlsx`         | Title screening: id, title.                                     |
| `step-3-review.xlsx`         | Abstract screening: id, abstract, keywords.                     |
| `step-4-review.xlsx` | Full-text screening: the research answers (solution name, RQa-RQh, IC2, IC3) as the evidence. |

Step 4 has a **single** sheet: the extracted research answers carry the evidence the reviewer
needs, so the verdict is recorded on that same row. It also has an `Agreement` column (Yes/No,
right after `llm_decision`) auditing whether the extracted answers themselves are correct,
separately from the include/exclude verdict.

Each sheet ends with three empty dropdown columns, the census-with-adjudication design:

| Column     | Filled by        | Scope                                                  |
|------------|------------------|--------------------------------------------------------|
| `Review 1` | First-pass       | **Every** row.                                         |
| `Review 2` | The adjudicator  | Only the rows where `Review 1` differs from the model. |
| `Finale`   | —                | The consolidated verdict, applied by step 8.           |

How the first pass is shared is a human convention the app does not enforce: steps 2 and 3 use
a single reviewer, while step 4 splits the rows among three reviewers by position (row modulo
3) and rotates the adjudication so nobody adjudicates their own review. Steps 6 to 8 read the
columns, not who filled them, so either arrangement works unchanged.

The `llm_decision` column carries the model's verdict for reference only; both reviewers work
blind by hiding the columns to their left (the adjudicator also hides `Review 1`).

**Reviewers save their filled copy as `step-<n>-review-reviewed.xlsx`** (and
`step-4-review-reviewed.xlsx`), which steps 6 to 8 read. Re-running step 5 therefore
never overwrites their work.

### Residual sheet

```
uv run python main.py --step 5 --residuals
```

When the previous step's human verdict admits records the model had excluded (its
**residuals**, see step 8), the step they move into is usually already under review, so they
cannot simply be appended. This exports a sheet holding **only** those records, with the same columns, to be reviewed
alongside the sheet already in progress (`step-3-residuals-review.xlsx`, and
`step-4-residuals-review.xlsx` for step 4).

Save it with the `-reviewed` suffix: steps 6 to 8 read it merged with the main
sheet, so the rows may stay in the supplementary file or be pasted into the main one, whichever
is convenient. Run it after step 8 (which records the residuals) and after re-running the
screening step for their origins (which produces the content the sheet shows).

## Adjudication report (step 6)

```
uv run python main.py --step 6
```

Both reviewers share one workbook, so this step builds no sheet: it reads each reviewed sheet
and reports which rows need `Review 2` (those where reviewer 1 differs from the model), which
are still pending, and warns about rows adjudicated without an underlying conflict. Writes
`.../tiebreak/pending.json`.

## Metrics (step 7)

```
uv run python main.py --step 7
```

Computes the LLM screening reliability from the reviewed sheets, writing
`.../metrics/metrics.json` plus a console summary. The gold standard is `Review 1`, with
`Review 2` breaking ties; the positive class is `include`.

Completeness is enforced **per step**: a step is scored only when its sheet is fully filled
(`Review 1` on every row and `Review 2` on every conflict), so a step still under review is
listed as not scored yet instead of blocking the ones already finished. The command fails only
when nothing at all can be scored. Reported per origin and pooled:

| Metric                            | Description                                          |
|-----------------------------------|------------------------------------------------------|
| Precision / Recall / F1           | LLM vs gold.                                        |
| Accuracy                          | Overall correctness of the LLM decisions.           |
| Confusion matrix                  | TP / FP / FN / TN counts.                           |
| Agreement                         | How often the LLM and `Review 1` decided the same.  |
| Conflicts                         | Rows where the LLM and `Review 1` disagree.         |
| Adjudication                      | How `Review 2` resolved those conflicts.            |

## Reconcile & residuals (step 8)

```
uv run python main.py --step 8
```

Applies the reviewers' consolidated verdict back to the pipeline. It reads any
`step-<n>-review-reviewed.xlsx` present in the review folder (absent ones are skipped), using
the columns described under [Review (step 5)](#review-step-5). The `id` must stay in the first
column; every other column is located by header name.

`Finale` is written onto each record as `human_decision`; the model's own `decision` is left
untouched so the metrics keep comparing model against human. The step warns (without failing)
about rows with no `Finale` and about any `Finale` that departs from the reviewer-1/reviewer-2
rule.

It also records the **final human tally on the root of each step's JSON**, right after the
model's own `included`/`excluded`: `human_included` and `human_excluded` (the reviewed records
the humans kept vs. dropped, so `human_included + human_excluded = reviewed`). The same figures,
plus provenance (`sheet`, `applied_at`, `recovered_from_exclude`, `dropped_from_include`), also
live in the `human_review` block. These per-origin counts feed the PRISMA flow numbers.

It then writes `.../residuals/step-<n>-residuals.json` with the **residuals**: records the
model excluded but the reviewers included. From that point on the next screening step treats
the human verdict as authoritative, so it picks the residuals up and drops whatever the
reviewers rejected. Re-run the next step per origin to process them:

```
uv run python main.py --origin <origin> --step 3
```

The step-3 manifest is incremental: records already screened keep their result, and only the
newly admitted ones are processed.
