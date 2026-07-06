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


def step2_title_screening(origin: str) -> dict:
    """Screen each step-1 record by its title; write data/<origin>/step-2.json."""
    data = json.loads(step_output_path(origin, 1).read_text(encoding="utf-8"))
    records = data["records"]
    agent, model_name = _build_agent()

    screened = []
    included = 0
    for record in records:
        result = Runner.run_sync(agent, f'Title: "{record.get("title", "")}"')
        decision: TitleDecision = result.final_output
        included += decision.decision == "include"
        screened.append({
            **record,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reason": decision.reason,
        })
        print(f"[{origin}] {record.get('id')}: {decision.decision} ({decision.confidence})")

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
    path = step_output_path(origin, 2)
    ensure_parent(path)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{origin}] step 2: {included}/{len(screened)} included -> {path}")
    return output
