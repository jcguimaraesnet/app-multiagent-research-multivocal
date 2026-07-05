# AGENTS.md

Working instructions for AI agents (Claude Code, Codex, Copilot, etc.) developing this
application.

## Project

`app-multiagent-research-multivocal` — a multi-agent application that automates the
research pipeline (search, screening, cataloguing) of the multivocal review supporting
the paper *"AI Solutions Applicable to Software Construction: A Rapid Multivocal
Review"* (UFRJ).

**Stack:**
- **OpenAI Agents SDK** — multi-agent orchestration. Docs: <https://openai.github.io/openai-agents-python/>
- **Scopus API** — academic-literature search.
- **Firecrawl API** — grey-literature scraping.

## Tooling — REQUIRED

- **Always use [uv](https://docs.astral.sh/uv/) for everything Python**: dependency
  management, virtual environments, and running code. Never call `pip` or bare `python`.
  - Add a dependency: `uv add <package>` (updates `pyproject.toml` and `uv.lock`).
  - Run code: `uv run <cmd>` (e.g., `uv run python main.py --origin scopus --step 1`).
  - Create/refresh the environment: `uv sync`.
  - `pyproject.toml` + `uv.lock` are the source of truth for dependencies. Do not add a
    `requirements.txt`.

## Teaching rule (OpenAI Agents SDK) — REQUIRED

Throughout the **entire creation and development** of this app, **explain the OpenAI
Agents SDK concepts as they are introduced**, so the author learns the framework while
it is being built. This is not optional documentation; it is a standing rule for every
step that touches the framework.

- The **first time** a framework primitive appears in the code (or in a design
  decision), explain: (1) what it is, (2) why it is used here, and (3) how it maps to
  the project's use case (search / screening / cataloguing).
- Cover, at minimum, the core primitives the SDK provides:
  - **Agents** — an LLM configured with instructions, tools, guardrails, handoffs.
  - **Tools** (function tools and hosted tools) — the actions an agent can take
    (e.g., call the Scopus API, scrape with Firecrawl).
  - **Runner** — executes agents and drives the agent loop (`Runner.run` / `run_sync`).
  - **Guardrails** — input/output validation that runs alongside agents.
  - **Handoffs** — delegation of control between agents.
  - **Sessions** — automatic conversation history / memory across runs.
  - **Tracing** — built-in run tracing for debugging and evaluation.
  - (…and any other primitive introduced, such as Context, output types, or model
    settings — the list above is a minimum, not a limit.)
- Prefer **linking to the official docs section** for each concept when explaining it.
- Keep explanations **grounded in this project**, not generic.
- Explanations are delivered **in the chat in pt-BR** (per the workspace convention);
  code, identifiers, and this repository stay in **en-US**.

## Conventions

- Make small, reviewable changes.
- **Do not commit or push unless explicitly asked.**
- **Never commit secrets.** API keys (Scopus, Firecrawl, OpenAI) must come from
  environment variables / a git-ignored `.env`; never hard-code them.
- Record sources and decisions that are not obvious from the code.
