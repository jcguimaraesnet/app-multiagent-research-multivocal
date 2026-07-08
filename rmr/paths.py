"""Filesystem locations for the pipeline.

The output of each (origin, step) is a JSON file at ``data/<origin>/<step-filename>``.
That file IS the state: a step's prerequisite check is simply the presence of the
previous step's output file (see ``steps.check_prerequisite``).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # the app/ repository root
PROTOCOL_DIR = PROJECT_ROOT / "protocol-settings"
DATA_DIR = PROJECT_ROOT / "data"

STEP_FILENAMES = {
    1: "step-1-initial-search.json",
    2: "step-2-screen-title.json",
    3: "step-3-screen-abstract.json",
    4: "step-4-screen-full.json",
}


def step_output_path(origin: str, step: int) -> Path:
    """Return the output path for (origin, step); see ``STEP_FILENAMES``.

    Step 1 (the model-independent search) lives at the origin root. The screening steps
    (2-4) live under the model-experiment subfolder, ``data/<origin>/<MODEL_EXPERIMENT>/``,
    so runs with different models are kept separate.
    """
    if step == 1:
        return DATA_DIR / origin / STEP_FILENAMES[step]
    from rmr import config  # local import avoids a circular import at module load
    return DATA_DIR / origin / config.model_experiment() / STEP_FILENAMES[step]


def full_path(origin: str, item_id: str) -> Path:
    """Full-text Markdown for one item: ``data/<origin>/content/full/<id>.md``.

    The single home for the full text, whatever its source: the grey scraped page (step 3)
    and the PDF-converted Markdown of scopus/hf (step 4) both land here.
    """
    return DATA_DIR / origin / "content" / "full" / f"{item_id}.md"


def pdf_path(origin: str, item_id: str) -> Path:
    """Manually downloaded full-text PDF: ``data/<origin>/content/pdf/<id>.pdf`` (step 4)."""
    return DATA_DIR / origin / "content" / "pdf" / f"{item_id}.pdf"


def abstract_path(origin: str, item_id: str) -> Path:
    """Captured/summarized content for one item (step 3), the durable, model-independent
    source of truth reused across screening re-runs: ``data/<origin>/content/abstract/<id>.json``."""
    return DATA_DIR / origin / "content" / "abstract" / f"{item_id}.json"


def summary_path(origin: str, item_id: str) -> Path:
    """Structured summary for one item: ``data/<origin>/summaries/<id>.json``."""
    return DATA_DIR / origin / "summaries" / f"{item_id}.json"


def validation_dir(step: int) -> Path:
    """Directory holding the screening-validation artifacts for the current model experiment:
    ``data/validation/<MODEL_EXPERIMENT>/step-<n>/`` (kept per experiment so validations of
    different models do not mix)."""
    from rmr import config  # local import avoids a circular import at module load
    return DATA_DIR / "validation" / config.model_experiment() / f"step-{step}"


def ensure_parent(path: Path) -> None:
    """Create the parent directory of ``path`` if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
