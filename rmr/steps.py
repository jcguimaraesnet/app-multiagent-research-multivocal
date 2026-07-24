"""Step registry, prerequisite enforcement, and dispatch.

Each step's output file is its record of completion. Step N (for N > 1) requires the
previous step's output file to exist for the same origin, otherwise it raises
``PrerequisiteError``. Handlers not yet implemented raise ``NotImplementedError``.
"""

from functools import partial

from rmr.paths import step_output_path
from rmr.screening import abstract as abstract_screening
from rmr.screening import fulltext as fulltext_screening
from rmr.screening import title as title_screening
from rmr.sources import grey, scopus

ORIGINS = ["scopus", "google", "github", "hf"]
SUBSTEPS = abstract_screening.SUBSTEPS  # valid only for step 3

STEPS = {
    1: "initial complete search",
    2: "title screening",
    3: "abstract & keywords screening",
    4: "full-text screening",
    5: "export blind human-review spreadsheets",
    6: "generate blind tie-break spreadsheets",
    7: "reconcile the human review and report the residuals",
    8: "compute screening metrics from human reviews",
}


class PrerequisiteError(Exception):
    """Raised when a step is invoked before its predecessor ran for that origin."""


# (origin, step) -> handler.
_HANDLERS = {
    ("scopus", 1): scopus.step1_initial_search,
    ("google", 1): partial(grey.step1_initial_search, "google"),
    ("github", 1): partial(grey.step1_initial_search, "github"),
    ("hf", 1): partial(grey.step1_initial_search, "hf"),
}

# Step 2 (title screening) is uniform across origins.
for _origin in ORIGINS:
    _HANDLERS[(_origin, 2)] = partial(title_screening.step2_title_screening, _origin)


def check_prerequisite(origin: str, step: int) -> None:
    if step == 1:
        return
    previous = step - 1
    previous_path = step_output_path(origin, previous)
    if not previous_path.exists():
        raise PrerequisiteError(
            f"step {step} ('{STEPS[step]}') for origin '{origin}' requires step {previous} "
            f"('{STEPS[previous]}') to run first (missing: {previous_path})"
        )


def run(origin: str, step: int, substep: str | None = None):
    if step == 3:
        return abstract_screening.step3_screening(origin, substep=substep)
    if step == 4:
        return fulltext_screening.step4_fulltext_screening(origin)
    handler = _HANDLERS.get((origin, step))
    if handler is None:
        raise NotImplementedError(
            f"step {step} ('{STEPS[step]}') for origin '{origin}' is not implemented yet"
        )
    return handler()
