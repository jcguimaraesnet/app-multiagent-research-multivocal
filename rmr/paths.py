"""Filesystem locations for the pipeline.

The artifacts of one model experiment live under ``data/screen/<MODEL_EXPERIMENT>/<origin>/``.
The output of each (origin, step) is a JSON file at that origin root; that file IS the state:
a step's prerequisite check is simply the presence of the previous step's output file
(see ``steps.check_prerequisite``).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # the app/ repository root
PROTOCOL_DIR = PROJECT_ROOT / "protocol-settings"
DATA_DIR = PROJECT_ROOT / "data"
# Per-origin search and screening artifacts live under data/screen/<MODEL_EXPERIMENT>/<origin>/;
# the cross-origin outputs (review, validation) stay directly under data/.
SCREEN_DIR = DATA_DIR / "screen"

STEP_FILENAMES = {
    1: "step-1-initial-search.json",
    2: "step-2-screen-title.json",
    3: "step-3-screen-abstract.json",
    4: "step-4-screen-full.json",
}


def origin_dir(origin: str) -> Path:
    """Root of one origin's artifacts for the current model experiment:
    ``data/screen/<MODEL_EXPERIMENT>/<origin>/``. Runs with different models stay separate."""
    from rmr import config  # local import avoids a circular import at module load
    return SCREEN_DIR / config.model_experiment() / origin


def step_output_path(origin: str, step: int) -> Path:
    """Return the output path for (origin, step); see ``STEP_FILENAMES``. Every step's JSON
    lives at the origin root ``data/screen/<MODEL_EXPERIMENT>/<origin>/``."""
    return origin_dir(origin) / STEP_FILENAMES[step]


def full_path(origin: str, item_id: str) -> Path:
    """Full-text Markdown for one item: ``.../<origin>/content/full/<id>.md``.

    The single home for the full text, whatever its source: the grey scraped page (step 3)
    and the PDF-converted Markdown of scopus/hf (step 4) both land here.
    """
    return origin_dir(origin) / "content" / "full" / f"{item_id}.md"


def pdf_path(origin: str, item_id: str) -> Path:
    """Manually downloaded full-text PDF: ``.../<origin>/content/pdf/<id>.pdf`` (step 4)."""
    return origin_dir(origin) / "content" / "pdf" / f"{item_id}.pdf"


def abstract_path(origin: str, item_id: str) -> Path:
    """Captured/summarized content for one item (step 3), the durable source reused across
    screening re-runs: ``.../<origin>/content/abstract/<id>.json``."""
    return origin_dir(origin) / "content" / "abstract" / f"{item_id}.json"


def summary_path(origin: str, item_id: str) -> Path:
    """Structured summary for one item: ``.../<origin>/summaries/<id>.json``."""
    return origin_dir(origin) / "summaries" / f"{item_id}.json"


def validation_dir(step: int) -> Path:
    """Directory holding the screening-validation artifacts for the current model experiment:
    ``data/validation/<MODEL_EXPERIMENT>/step-<n>/`` (kept per experiment so validations of
    different models do not mix)."""
    from rmr import config  # local import avoids a circular import at module load
    return DATA_DIR / "validation" / config.model_experiment() / f"step-{step}"


def review_dir() -> Path:
    """Directory for the blind human-review spreadsheets of the current model experiment:
    ``data/review/<MODEL_EXPERIMENT>/`` (step 5). Kept per experiment so review sheets of
    different models do not mix."""
    from rmr import config  # local import avoids a circular import at module load
    return DATA_DIR / "review" / config.model_experiment()


def ensure_parent(path: Path) -> None:
    """Create the parent directory of ``path`` if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
