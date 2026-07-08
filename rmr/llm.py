"""Shared OpenRouter model factory for the screening agents.

The model is served through OpenRouter (OpenAI-compatible). OPENROUTER_MODEL is optional:
when empty, OpenRouter uses the account's default model. Set it (a model slug or an
OpenRouter preset slug) to pin a specific model.
"""

import os

from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from rmr import config

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def openrouter_model():
    """Return (model, model_name) for the Agents SDK, backed by OpenRouter."""
    api_key = config.require_env("OPENROUTER_API_KEY")
    model_name = os.environ.get("OPENROUTER_MODEL", "").strip()
    client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client), model_name
