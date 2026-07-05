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

## Data layout

```
data/
  scopus/
    step-1.json   # identification search (records + query + totals)
    step-2.json
    ...
  google/
  github/
  pwc/
```

`data/` is git-ignored; it is produced at runtime and not committed.

## Protocol settings

The search terms are read from `protocol-settings/2-search-string.json` (a single PICOC
term set applied to all origins). Invariant execution rules (Scopus field scope, year
window, subject area, document type, language, query splitting for grey literature) live
in the code, not in the settings files.

## Implementation status

- **Scopus / step 1**: implemented (direct Scopus Search API call).
- Other origins and steps: not yet implemented (the CLI reports this explicitly).

Steps 2 to 4 (LLM-assisted screening) will be built with the **OpenAI Agents SDK**
(<https://openai.github.io/openai-agents-python/>); see `AGENTS.md` for the framework
teaching rule that applies to that work.
