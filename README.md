# app-multiagent-research-multivocal

Multi-agent application to automate the research pipeline of the multivocal review
(search, screening, and cataloguing) supporting the paper
*"AI Solutions Applicable to Software Construction: A Rapid Multivocal Review"* (UFRJ).

The pipeline is run from the command line, one **origin** and one **step** at a time.

## Requirements

- Python 3.11+ managed by [uv](https://docs.astral.sh/uv/).
- Create the environment / install dependencies: `uv sync`.
- A `.env` file at the repository root with the API keys (copy from `.env.example`).
  Scopus step 1 needs `SCOPUS_API_KEY`; the screening steps (2-4) need `MODEL_EXPERIMENT`
  set (the subfolder name for that model's outputs) and `OPENROUTER_API_KEY`.

This project uses **uv** for everything (dependencies, virtual environment, running).
Use `uv add <pkg>` to add a dependency and `uv run <cmd>` to run code.

## Usage

```
uv run python main.py --origin <scopus|google|github|pwc> --step <1|2|3|4>
```

Both parameters are **required**.

### Origins

| Value    | Source                                                                 |
|----------|------------------------------------------------------------------------|
| `scopus` | Scopus (academic literature), via the Scopus Search API                |
| `google` | Google general web (grey literature), via Firecrawl                     |
| `github` | GitHub, via Firecrawl with `site:github.com`                            |
| `hf`     | Hugging Face Papers, via Firecrawl with `site:huggingface.co/papers`    |

The `hf` origin replaces Papers With Code, which was discontinued during the study and
now redirects to Hugging Face Papers. In the manuscript this substitution is noted in the
text; the PRISMA flow and Table 1 keep their original labels.

### Steps

| Step | Meaning                          |
|------|----------------------------------|
| `1`  | Initial complete search          |
| `2`  | Title screening                  |
| `3`  | Abstract & keywords screening    |
| `4`  | Full-text screening              |

## Title recovery (step 1)

Search engines truncate result titles with an ellipsis, which weakens title screening. So
step 1, right after the grey search, recovers the full title and stores it in the step-1 output.
Step 2 is then pure title screening, with no network access of its own.

- `hf`: fetched from the free arXiv API (HF Papers are arXiv papers).
- `google`/`github`: a free HTTP GET reads `og:title`/`<title>`; only pages behind
  anti-bot protection (Cloudflare/JS challenge) fall back to a Firecrawl scrape. GitHub
  needs no fallback; a small share of Google pages do. Titles that cannot be recovered
  keep their truncated form.
- `scopus`: titles already come complete from the Search API and are left untouched.

## Step ordering rule

Each step consumes the previous step's result for the **same origin**, so steps must
run in order. A step's output file is its record of completion:

```
data/<origin>/step-<n>-<name>.json
```

Step `N` (for `N > 1`) requires the previous step's output file to exist. If it does
not, the command fails with a clear error and a non-zero exit code, for example:

```
$ uv run python main.py --origin scopus --step 3
Error: step 3 ('abstract & keywords screening') for origin 'scopus' requires step 2
('title screening') to run first (missing: data/scopus/step-2-screen-title.json)
```

Step `1` has no prerequisite. Invalid `--origin`/`--step` values are rejected by the
CLI (exit code 2).

## Step 3 substeps

Step 3 (abstract & keywords screening) runs in three idempotent phases, selectable with the
optional `--substep`:

```
uv run python main.py --origin <origin> --step 3 [--substep scrape|summary|screen]
```

The captured/summarized content is stored per item in `content/abstract/<id>.json` (title,
link, abstract or summary, keywords, and per-origin extras). This is the durable,
**model-independent** source of truth, kept separate from the model-dependent decisions, so
the screening can be re-run with a different LLM while reusing it. The `step-3-screen-abstract.json` manifest
keeps only `id`, `status`, a light `data` (title + link), and the `screening` result.

- `scrape`: acquire content, by origin (reuses the abstract file if already populated).
  - `google`/`github`: Firecrawl scrape of the page -> `content/full/<id>.md` (status -> scraped).
  - `hf`: HF Papers are arXiv papers, so the fields (abstract, authors, publication date,
    PDF link) are fetched from the free arXiv API in batches into the abstract file (scraped).
  - `scopus`: the authenticated Scopus gateway writes the `abstract` and author keywords to
    the abstract file; academic skips `summarized`, so the status goes straight to `scraped`.
    Needs a valid Scopus session cookie in `data/.scopus_cookie.txt` (git-ignored).
- `summary`: `google`/`github` condense the scraped page into a summary + keywords with the
  LLM; `hf` only generates keywords (arXiv gives the abstract but no keywords). Written to the
  abstract file, reusing it if already present. Not applicable to academic (status -> summarized).
- `screen`: assess IC1-IC5 and EC3/EC4/EC5 over the abstract/summary and keywords (read from
  the abstract file). Each criterion gets a verdict (`met`/`not_met`/`unclear`) and a short
  note (empty when unclear); EC3 is set by code, the rest by the LLM. The overall `decision`
  and `reason` are derived from the criteria (exclude if any IC is `not_met` or any EC is `met`).

Idempotency is driven by the per-record `status` in the step-3 manifest (grey:
`pending -> scraped -> summarized -> screened`; academic: `pending -> scraped -> screened`).
Because scrape/summary reuse `content/abstract/<id>.json`, deleting the step-3 manifest and re-running
re-screens with a new model without re-scraping or re-summarizing.

Omit `--substep` to run all three in order. Each phase skips work already done, so a re-run
continues from where it stopped. A page that cannot be retrieved is excluded as EC3.

## Step 4 (full-text screening)

Implemented for all origins. For each step-3 survivor (decision = include), the full text is
located, then two LLM calls run over it, in a single pass (no `--substep`):

```
uv run python main.py --origin <scopus|google|github|hf> --step 4
```

1. **answer** (status -> `answered`): extract the research-question answers RQa-RQh. Each is
   a `note` (concise, objective) plus a `value` classification from a fixed set (RQf takes a
   list; the rest one value); the set is enforced by the model's structured output. The result
   is stored under the record's `answers` object.
2. **screen** (status -> `screened`): the final IC/EC screening, given **both** the full text
   and the research answers as context. Unlike step 3, every criterion is **binary** (`met` /
   `not_met`, never `unclear`) with a short note. IC2 also records the solution `type` (agent,
   tool, language model, extension, IDE, technique/solution) and the coding-phase
   `software_engineering_activity`; IC3 records its `type` (primary study / empirical case).
   A field that fits none of its options is left empty and its criterion is `not_met`.

How the full text is obtained differs by origin:

- **scopus**: full texts are paywalled, so the PDFs are downloaded manually into
  `data/scopus/content/pdf/<id>.pdf`. If a PDF is missing, the record stays `pending` (run
  once with no PDFs to get the manifest and the exact filenames it expects, drop the PDFs
  in, then re-run). Each PDF is converted to `data/scopus/content/full/<id>.md` with
  **pymupdf4llm** (an existing conversion is reused; an empty extraction, e.g. a scanned
  PDF, stays `pending` with a warning). Status: `pending -> converted -> answered -> screened`.
- **hf**: HF Papers are arXiv papers, so the PDF is downloaded automatically from the arXiv
  link captured in step 3 into `data/hf/content/pdf/<id>.pdf` and converted the same way as
  scopus. A transient download error stays `pending` (retried later); a paper that is
  permanently gone (withdrawn / HTTP 404) is excluded via EC3 (content availability). Status:
  `pending -> converted -> answered -> screened`.
- **google/github**: the full page was already scraped in step 3 to
  `data/<origin>/content/full/<id>.md`, so step 4 reads it directly (no download/conversion). A
  missing/empty scrape stays `pending`. Status: `pending -> answered -> screened`.

The full text sent to the model is capped at 150000 characters (logged when it is
truncated). The manifest is saved after every phase, so a re-run resumes cleanly (an
answered-but-not-screened record only runs screen; a screened record is skipped).

## Screening validation (steps 2, 3, 4)

To report the reliability of the LLM screening (precision / recall / F1 and rater
agreement) without labelling the whole pool, `validate.py` draws a **stratified** sample and
has two humans label it blind:

```
uv run python validate.py sample --step <2|3|4> [--seed 42] [--margin 0.08] [--overlap 120]
uv run python validate.py score  --step <2|3|4>
```

- **Design.** Precision is estimated from a random sample of the LLM-*include* stratum
  (sample size from the finite-population formula at `--margin`); recall is measured from a
  full **census** of the LLM-*exclude* stratum, where the rare false negatives hide, so it is
  essentially exact. Excludes are few (step 2: 190; step 3: ~130), which makes the census
  cheap. Sampling is reproducible (fixed `--seed`).
- **Two raters.** Step 2 (titles are cheap): both raters label the whole sample (full
  double-labelling). Steps 3 and 4 (costlier): both label a stratified `--overlap` subset for
  inter-rater reliability, and the rest is split between them. Sheets are blind (no LLM
  decision, shuffled order).
- **What each sheet shows.** Step 2: the title. Step 3: title + abstract/summary + keywords.
  Step 4 (full-text review): title + link + a `source` column with the repo-relative path to
  the full text (`content/full/<id>.md`), which
  the rater opens to read.
- **`sample`** writes `data/validation/<MODEL_EXPERIMENT>/step-<n>/rater-A.csv`, `rater-B.csv`
  (raters fill `human_decision` = include/exclude) and `key.json` (kept aside, holds the LLM
  decisions). Validation is scoped to the active `MODEL_EXPERIMENT`, matching the screening it checks.
- **`score`** builds the gold standard (overlap agreements + adjudicated disagreements +
  single-rater labels), then reports inter-rater agreement (percent, Cohen's kappa, and
  Gwet's AC1, which is robust to the prevalence paradox) and precision/recall/F1 vs the gold,
  per origin and pooled, with 95% CIs, into `metrics.json`. Overlap disagreements are written
  to `adjudication-template.csv`; fill `adjudicated_decision`, save as `adjudication.csv`, and
  re-run `score`.

## Data layout

```
data/
  <origin>/                       # scopus | google | github | hf
    step-1-initial-search.json    # identification search (grey titles already recovered)
    content/full/<id>.md          # full-text markdown: grey scrape (step 3) + pdf conversion (step 4)
    content/abstract/<id>.json    # step 3 captured/summarized content (all origins)
    content/pdf/<id>.pdf          # step 4: full-text PDF (scopus manual, hf auto from arXiv)
    <MODEL_EXPERIMENT>/           # e.g. deepseek-v4-fast: one model's screening outputs
      step-2-screen-title.json    # title screening (decisions)
      step-3-screen-abstract.json # step 3 manifest (status + decisions)
      step-4-screen-full.json     # step 4 manifest + full-text decisions
  validation/
    <MODEL_EXPERIMENT>/           # validation is per experiment too
      step-<2|3|4>/               # screening-validation sample, blind sheets, key, metrics
```

Step 1 and the captured content (`content/`) are **model-independent** and live at the origin
root, shared across experiments. The screening outputs (steps 2-4) are **model-dependent** and
live under a per-experiment subfolder named by the `MODEL_EXPERIMENT` env var (not sent to
OpenRouter; it only structures the folders), so re-running the screening with a different model
keeps each run's decisions separate while reusing the same step-1 search and captured content.

The captured content and the screening decisions are two separate stores.
`content/abstract/<id>.json` is the model-independent content record (title, link,
abstract/summary, keywords, per-origin extras). Each `step-3-screen-abstract.json` /
`step-4-screen-full.json` record keeps `id`, `status`, a light `data` (title + link), and the
model-dependent `screening` (decision, confidence, reason, per-criterion verdicts). Grey
sources keep the raw scraped page and PDF origins the PDF-converted Markdown, both under
`content/full/<id>.md`; the downloaded PDFs live under `content/pdf`.

`data/` is git-ignored; it is produced at runtime and not committed.

## Protocol settings

The search terms are read from `protocol-settings/2-search-string.json` (a single PICOC
term set applied to all origins). Invariant execution rules (Scopus field scope, year
window, subject area, document type, language, query splitting for grey literature) live
in the code, not in the settings files.

## Implementation status

- **Step 1** (initial search): implemented for all origins (Scopus Search API; grey via Firecrawl).
- **Step 2** (title screening): implemented for all origins (OpenAI Agents SDK via OpenRouter).
- **Step 3** (abstract & keywords screening): implemented for all origins (scrape/summary/screen).
- **Step 4** (full-text screening): implemented for all origins -> final LLM screening.
  scopus (manual PDFs) and hf (auto-downloaded arXiv PDFs) go through pymupdf4llm Markdown;
  google/github reuse the step-3 scraped page.

The LLM screening steps use the **OpenAI Agents SDK**
(<https://openai.github.io/openai-agents-python/>) through OpenRouter; see `AGENTS.md` for
the framework teaching rule that applies to that work.
