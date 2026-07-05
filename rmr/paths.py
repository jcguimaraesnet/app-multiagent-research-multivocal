"""Filesystem locations for the pipeline.

The output of each (origin, step) is a JSON file at ``data/<origin>/step-<n>.json``.
That file IS the state: a step's prerequisite check is simply the presence of the
previous step's output file (see ``steps.check_prerequisite``).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # the app/ repository root
PROTOCOL_DIR = PROJECT_ROOT / "protocol-settings"
DATA_DIR = PROJECT_ROOT / "data"


def step_output_path(origin: str, step: int) -> Path:
    """Return ``data/<origin>/step-<step>.json``."""
    return DATA_DIR / origin / f"step-{step}.json"


def ensure_parent(path: Path) -> None:
    """Create the parent directory of ``path`` if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
