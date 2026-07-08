"""Environment and protocol-settings loading.

Secrets come from the git-ignored ``.env`` at the repository root; the search terms
come from ``protocol-settings/2-search-string.json``. Invariant execution rules
(field scope, filters, boolean operators) live in the source modules, not here.
"""

import json
import os

from rmr.paths import PROJECT_ROOT, PROTOCOL_DIR

_ENV_LOADED = False


def load_dotenv(path=None) -> None:
    """Load KEY=VALUE lines from ``.env`` into ``os.environ`` (without overriding)."""
    global _ENV_LOADED
    env_path = path or (PROJECT_ROOT / ".env")
    try:
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass
    _ENV_LOADED = True


def require_env(name: str) -> str:
    """Return a required environment variable, or raise if it is missing/empty."""
    if not _ENV_LOADED:
        load_dotenv()
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            f"Set it in {PROJECT_ROOT / '.env'} (see .env.example)."
        )
    return value


def model_experiment() -> str:
    """Return ``MODEL_EXPERIMENT``: the subfolder name that isolates one model's screening
    outputs (steps 2-4). It is NOT sent to OpenRouter; it only structures the data folders,
    so runs with different models stay separate."""
    return require_env("MODEL_EXPERIMENT")


def load_search_string() -> dict:
    """Return the PICOC term lists from ``protocol-settings/2-search-string.json``."""
    path = PROTOCOL_DIR / "2-search-string.json"
    data = json.loads(open(path, encoding="utf-8").read())
    return data["search_string"]
