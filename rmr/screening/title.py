"""Step 2: title screening.

The first LLM step. It uses the OpenAI Agents SDK:
- An **Agent** is an LLM configured with instructions (our title-screening prompt) and a
  typed output. Docs: https://openai.github.io/openai-agents-python/agents/
- **Runner** executes the agent (the agent loop). Docs: https://openai.github.io/openai-agents-python/running_agents/
- **output_type** (a Pydantic model) makes the SDK return a validated, structured result
  instead of free text. Docs: https://openai.github.io/openai-agents-python/agents/#output-types
- The model is served through OpenRouter (OpenAI-compatible) via an AsyncOpenAI client
  wrapped in **OpenAIChatCompletionsModel**.

The decision is made from the TITLE ONLY (the protocol's title-screening stage); the link
and other metadata are carried forward untouched for later steps but are not shown to the
model here.
"""

import json
import os
from datetime import datetime, timezone
from typing import Literal

from agents import (
    Agent,
    ModelSettings,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)
from openai import AsyncOpenAI
from pydantic import BaseModel

from rmr import config
from rmr.content import arxiv, titles
from rmr.paths import PROJECT_ROOT, ensure_parent, step_output_path

# Tracing defaults to OpenAI's backend; we run through OpenRouter, so disable it.
set_tracing_disabled(True)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = ""
PROMPT_PATH = PROJECT_ROOT / "prompts" / "step2-title-screening.md"


class TitleDecision(BaseModel):
    """Structured output of the title screener."""

    decision: Literal["include", "exclude"]
    confidence: Literal["low", "medium", "high"]
    reason: str


def _build_agent():
    api_key = config.require_env("OPENROUTER_API_KEY")
    model_name = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    model = OpenAIChatCompletionsModel(model=model_name, openai_client=client)
    agent = Agent(
        name="Title screener",
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        model=model,
        model_settings=ModelSettings(temperature=0.2),
        output_type=TitleDecision,
    )
    return agent, model_name


def _enrich_hf_titles(records: list[dict]) -> None:
    """HF search titles come truncated from the search snippet; replace them with the full
    arXiv title, since HF Papers are arXiv papers."""
    id_by_item = {r["id"]: arxiv.arxiv_id_from_link(r.get("link", "")) for r in records}
    details = arxiv.fetch_many(list(id_by_item.values()))
    enriched = 0
    for record in records:
        found = details.get(id_by_item[record["id"]])
        if found and found.get("title"):
            record["title"] = found["title"]
            enriched += 1
    print(f"[hf] step 2: enriched {enriched}/{len(records)} titles from arXiv")


def _enrich_grey_titles(origin: str, records: list[dict]) -> None:
    """Google/GitHub search titles are truncated by the engine; recover the full page
    title (free GET, Firecrawl fallback for anti-bot pages)."""
    full = titles.fetch_titles(records)
    enriched = 0
    for record in records:
        recovered = full.get(record["id"])
        if recovered:
            record["title"] = recovered
            enriched += 1
    print(f"[{origin}] step 2: enriched {enriched}/{len(records)} titles")


def _enrich_titles(origin: str, records: list[dict]) -> None:
    """Recover full titles before screening, since the search snippet truncates them.
    Scopus titles already come complete from the Search API, so they are left untouched."""
    if origin == "hf":
        _enrich_hf_titles(records)
    elif origin in ("google", "github"):
        _enrich_grey_titles(origin, records)


def _load_existing(path) -> dict:
    """Return {id: screened_record} from a prior step-2.json, for idempotent re-runs."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {r["id"]: r for r in data.get("records", []) if "decision" in r}


def step2_title_screening(origin: str) -> dict:
    """Screen each step-1 record by its title; write data/<origin>/step-2.json.

    Idempotent per record: records already screened in a prior run are kept as-is, so a
    re-run only screens (and re-enriches titles for) what is still pending. Delete the
    step-2.json to force a full re-screen.
    """
    data = json.loads(step_output_path(origin, 1).read_text(encoding="utf-8"))
    records = data["records"]

    path = step_output_path(origin, 2)
    ensure_parent(path)
    existing = _load_existing(path)
    pending = [r for r in records if r["id"] not in existing]
    if existing:
        print(f"[{origin}] step 2: {len(existing)} already screened, {len(pending)} pending")

    _enrich_titles(origin, pending)  # only recover titles for records still to be screened
    agent, model_name = _build_agent()

    screened: list[dict] = []

    def save() -> dict:
        included = sum(r["decision"] == "include" for r in screened)
        output = {
            "origin": origin,
            "step": 2,
            "model": model_name,
            "screened_at": datetime.now(timezone.utc).isoformat(),
            "count": len(screened),
            "included": included,
            "excluded": len(screened) - included,
            "records": screened,
        }
        path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        return output

    for record in records:
        if record["id"] in existing:
            screened.append(existing[record["id"]])  # keep the prior decision, in order
            continue
        result = Runner.run_sync(agent, f'Title: "{record.get("title", "")}"')
        decision: TitleDecision = result.final_output
        screened.append({
            **record,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reason": decision.reason,
        })
        save()  # persist after every screened record, so a re-run loses nothing
        print(f"[{origin}] {record.get('id')}: {decision.decision} ({decision.confidence})")

    output = save()
    print(f"[{origin}] step 2: {output['included']}/{output['count']} included -> {path}")
    return output
