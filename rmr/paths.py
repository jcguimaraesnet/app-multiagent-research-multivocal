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


def content_path(origin: str, item_id: str) -> Path:
    """Raw acquired content for one item: ``data/<origin>/content/<id>.md``."""
    return DATA_DIR / origin / "content" / f"{item_id}.md"


def pdf_path(origin: str, item_id: str) -> Path:
    """Manually downloaded full-text PDF: ``data/<origin>/content/pdf/<id>.pdf`` (step 4)."""
    return DATA_DIR / origin / "content" / "pdf" / f"{item_id}.pdf"


def markdown_path(origin: str, item_id: str) -> Path:
    """Full-text Markdown converted from the PDF: ``data/<origin>/content/markdown/<id>.md``."""
    return DATA_DIR / origin / "content" / "markdown" / f"{item_id}.md"


def summary_path(origin: str, item_id: str) -> Path:
    """Structured summary for one item: ``data/<origin>/summaries/<id>.json``."""
    return DATA_DIR / origin / "summaries" / f"{item_id}.json"


def validation_dir(step: int) -> Path:
    """Directory holding the screening-validation artifacts: ``data/validation/step-<n>/``."""
    return DATA_DIR / "validation" / f"step-{step}"


def ensure_parent(path: Path) -> None:
    """Create the parent directory of ``path`` if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
