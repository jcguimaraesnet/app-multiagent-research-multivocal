# app-multiagent-research-multivocal

Multi-agent application to automate the research pipeline of the multivocal review
(search, screening, and cataloguing) supporting the paper
*"AI Solutions Applicable to Software Construction: A Rapid Multivocal Review"* (UFRJ).

The pipeline is run from the command line, one **origin** and one **step** at a time.

## Requirements

- Python 3.11+ managed by [uv](https://docs.astral.sh/uv/).
- Create the environment / install dependencies: `uv sync`.
- A `.env` file at the repository root with the API keys (copy from `.env.example`).
  Scopus step 1 needs `SCOPUS_API_KEY`.

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

## Title recovery (step 2)

Search engines truncate result titles with an ellipsis, which weakens title screening.
Before screening, step 2 recovers the full title:

- `hf`: fetched from the free arXiv API (HF Papers are arXiv papers).
- `google`/`github`: a free HTTP GET reads `og:title`/`<title>`; only pages behind
  anti-bot protection (Cloudflare/JS challenge) fall back to a Firecrawl scrape. GitHub
  needs no fallback; a small share of Google pages do. Titles that cannot be recovered
  keep their truncated form.
- `scopus`: titles already come complete from the Search API and are left untouched.

The recovered title is written into `step-2.json`, so step 3 (`data.title`) inherits it.

## Step ordering rule

Each step consumes the previous step's result for the **same origin**, so steps must
run in order. A step's output file is its record of completion:

```
data/<origin>/step-<n>.json
```

Step `N` (for `N > 1`) requires `data/<origin>/step-<N-1>.json` to exist. If it does
not, the command fails with a clear error and a non-zero exit code, for example:

```
$ uv run python main.py --origin scopus --step 3
Error: step 3 ('abstract & keywords screening') for origin 'scopus' requires step 2
('title screening') to run first (missing: data/scopus/step-2.json)
```

Step `1` has no prerequisite. Invalid `--origin`/`--step` values are rejected by the
CLI (exit code 2).

## Step 3 substeps

Step 3 (abstract & keywords screening) runs in three idempotent phases, selectable with the
optional `--substep`:

```
uv run python main.py --origin <origin> --step 3 [--substep scrape|summary|screen]
```

- `scrape`: acquire content, by origin.
  - `google`/`github`: Firecrawl scrape of the page -> `content/<id>.md` (status -> scraped).
  - `hf`: HF Papers are arXiv papers, so the fields (abstract, authors, publication date,
    PDF link) are fetched from the free arXiv API in batches (status -> scraped).
  - `scopus`: the authenticated Scopus gateway writes the `abstract` and author keywords
    inline; academic skips `summarized`, so the status goes straight to `scraped`. Needs a
    valid Scopus session cookie in `data/.scopus_cookie.txt` (git-ignored).
- `summary`: `google`/`github` condense the scraped page into a summary + keywords with the
  LLM; `hf` only generates keywords (arXiv gives the abstract but no keywords). Not
  applicable to academic sources (status -> summarized).
- `screen`: assess IC1-IC5 and EC3/EC4/EC5 over the abstract/summary and keywords. Each
  criterion gets a verdict (`met`/`not_met`/`unclear`) and a short note (empty when unclear);
  EC3 is set by code, the rest by the LLM. The overall `decision` and `reason` are derived
  from the criteria (exclude if any IC is `not_met` or any EC is `met`).

Idempotency is driven by the per-record `status` in `step-3.json` (grey:
`pending -> scraped -> summarized -> screened`; academic: `pending -> scraped -> screened`),
not by file presence.

Omit `--substep` to run all three in order. Each phase skips work already done, so a re-run
continues from where it stopped. A page that cannot be retrieved is excluded as EC3.

## Step 4 (full-text screening)

Implemented for all origins. For each step-3 survivor (decision = include), the full text is
located and the final IC/EC screening is run over it, in a single pass (no `--substep`):

```
uv run python main.py --origin <scopus|google|github|hf> --step 4
```

How the full text is obtained differs by origin:

- **scopus**: full texts are paywalled, so the PDFs are downloaded manually into
  `data/scopus/content/pdf/<id>.pdf`. If a PDF is missing, the record stays `pending` (run
  once with no PDFs to get the manifest and the exact filenames it expects, drop the PDFs
  in, then re-run). Each PDF is converted to `data/scopus/content/markdown/<id>.md` with
  **pymupdf4llm** (an existing conversion is reused; an empty extraction, e.g. a scanned
  PDF, stays `pending` with a warning). Status: `pending -> converted -> screened`.
- **hf**: HF Papers are arXiv papers, so the PDF is downloaded automatically from the arXiv
  link captured in step 3 into `data/hf/content/pdf/<id>.pdf` and converted the same way as
  scopus. A transient download error stays `pending` (retried later); a paper that is
  permanently gone (withdrawn / HTTP 404) is excluded via EC3 (content availability). Status:
  `pending -> converted -> screened`.
- **google/github**: the full page was already scraped in step 3 to
  `data/<origin>/content/<id>.md`, so step 4 reads it directly (no download/conversion). A
  missing/empty scrape stays `pending`. Status: `pending -> screened`.

The full text sent to the model is capped at 60000 characters (logged when it is
truncated). The manifest is saved after every item, so a re-run only screens what is not
yet `screened`.

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
  the full text (`content/<id>.md` for grey, `content/markdown/<id>.md` for scopus/hf), which
  the rater opens to read.
- **`sample`** writes `data/validation/step-<n>/rater-A.csv`, `rater-B.csv` (raters fill
  `human_decision` = include/exclude) and `key.json` (kept aside, holds the LLM decisions).
- **`score`** builds the gold standard (overlap agreements + adjudicated disagreements +
  single-rater labels), then reports inter-rater agreement (percent, Cohen's kappa, and
  Gwet's AC1, which is robust to the prevalence paradox) and precision/recall/F1 vs the gold,
  per origin and pooled, with 95% CIs, into `metrics.json`. Overlap disagreements are written
  to `adjudication-template.csv`; fill `adjudicated_decision`, save as `adjudication.csv`, and
  re-run `score`.

## Data layout

```
data/
  <origin>/                 # scopus | google | github | hf
    step-1.json             # identification search
    step-2.json             # title screening (decisions)
    content/<id>.md         # step 3 scrape: raw scraped page (grey only)
    step-3.json             # manifest + inline summaries + decisions (source of truth)
    content/pdf/<id>.pdf     # step 4: full-text PDF (scopus manual, hf auto from arXiv)
    content/markdown/<id>.md # step 4: PDF converted to Markdown (scopus, hf)
    step-4.json             # step 4 manifest + full-text decisions
  validation/
    step-<2|3>/             # screening-validation sample, blind sheets, key, metrics
```

The step-3 manifest is the source of truth. Each record has `id` and `status` at the root,
the scraped/source fields under `data` (title, link, abstract/summary, keywords, and
per-literature extras), and the screening result under `screening` (decision, confidence,
reason, and per-criterion verdicts). The only per-item file is the grey scraped page
(`content/<id>.md`, large); academic sources have no file (the gateway data lives in
`data`). Step 4 will use per-link files.

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
