"""Shared chat-model factory for the screening agents.

The agents talk to any OpenAI-compatible endpoint (OpenRouter, Azure OpenAI's ``/openai/v1``
surface, the OpenAI API, ...). The provider is chosen entirely by environment variables, so
switching providers needs no code change:

- ``LLM_BASE_URL``  the OpenAI-compatible base URL (default: OpenRouter). For Azure use the
                    resource's v1 endpoint, e.g.
                    ``https://<resource>.services.ai.azure.com/openai/v1``.
- ``LLM_API_KEY``   the API key for that endpoint.
- ``LLM_MODEL``     the model / deployment name (for Azure, the deployment name). Empty means
                    the endpoint's default, where the provider allows it.
- ``LLM_API``       ``chat`` (Chat Completions, the default; OpenRouter) or ``responses``
                    (the Responses API). Some models (e.g. Azure gpt-5 "pro") only serve the
                    Responses API and reject ``/chat/completions``.

For backward compatibility, ``OPENROUTER_API_KEY`` / ``OPENROUTER_MODEL`` are used when the
``LLM_*`` variables are not set.
"""

import os

from agents import ModelSettings, OpenAIChatCompletionsModel, OpenAIResponsesModel
from openai import AsyncOpenAI

from rmr import config

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def model_settings(max_tokens=None):
    """Shared ModelSettings for the agents. Temperature comes from ``LLM_TEMPERATURE``
    (default 0.2); set it empty for models that reject a custom temperature (e.g. gpt-5
    'pro'), so it is omitted from the request."""
    config.load_dotenv()
    kwargs = {}
    temperature = os.environ.get("LLM_TEMPERATURE", "0.2").strip()
    if temperature:
        kwargs["temperature"] = float(temperature)
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    return ModelSettings(**kwargs)


def chat_model():
    """Return (model, model_name) for the Agents SDK, backed by the configured endpoint."""
    config.load_dotenv()
    base_url = os.environ.get("LLM_BASE_URL", "").strip() or DEFAULT_BASE_URL
    api_key = (os.environ.get("LLM_API_KEY", "").strip()
               or os.environ.get("OPENROUTER_API_KEY", "").strip())
    if not api_key:
        raise RuntimeError("Set LLM_API_KEY (or OPENROUTER_API_KEY) in .env")
    model_name = (os.environ.get("LLM_MODEL", "").strip()
                  or os.environ.get("OPENROUTER_MODEL", "").strip())
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    api = os.environ.get("LLM_API", "chat").strip().lower()
    model_cls = OpenAIResponsesModel if api == "responses" else OpenAIChatCompletionsModel
    return model_cls(model=model_name, openai_client=client), model_name
