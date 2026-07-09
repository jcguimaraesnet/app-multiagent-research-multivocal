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
from datetime import datetime, timezone
from typing import Literal

from agents import Agent, Runner, set_tracing_disabled
from pydantic import BaseModel

from rmr.llm import chat_model, model_settings
from rmr.paths import PROJECT_ROOT, ensure_parent, step_output_path

# Tracing defaults to OpenAI's backend; we use a custom endpoint, so disable it.
set_tracing_disabled(True)

PROMPT_PATH = PROJECT_ROOT / "prompts" / "step2-title-screening.md"
# Cap the output budget so the provider reserves credit for a small completion (without an
# explicit cap some providers reserve the model's full output window, tripping a 402/limit).
TITLE_MAX_TOKENS = 500


class TitleDecision(BaseModel):
    """Structured output of the title screener."""

    decision: Literal["include", "exclude"]
    confidence: Literal["low", "medium", "high"]
    reason: str


def _build_agent():
    model, model_name = chat_model()
    agent = Agent(
        name="Title screener",
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        model=model,
        model_settings=model_settings(max_tokens=TITLE_MAX_TOKENS),
        output_type=TitleDecision,
    )
    return agent, model_name


def _load_existing(path) -> dict:
    """Return {id: screened_record} from a prior step-2 output, for idempotent re-runs."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {r["id"]: r for r in data.get("records", []) if "decision" in r}


def step2_title_screening(origin: str) -> dict:
    """Screen each step-1 record by its title; write data/<origin>/step-2-screen-title.json.

    Idempotent per record: records already screened in a prior run are kept as-is, so a
    re-run only screens what is still pending. Delete the step-2 output to force a full
    re-screen. Titles are already complete here (recovered at step 1), so this stage is
    pure LLM screening with no network access of its own.
    """
    data = json.loads(step_output_path(origin, 1).read_text(encoding="utf-8"))
    records = data["records"]

    path = step_output_path(origin, 2)
    ensure_parent(path)
    existing = _load_existing(path)
    pending = [r for r in records if r["id"] not in existing]
    if existing:
        print(f"[{origin}] step 2: {len(existing)} already screened, {len(pending)} pending")

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
