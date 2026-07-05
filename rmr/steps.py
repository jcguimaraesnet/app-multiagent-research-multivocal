"""Step registry, prerequisite enforcement, and dispatch.

Each step's output file is its record of completion. Step N (for N > 1) requires the
previous step's output file to exist for the same origin, otherwise it raises
``PrerequisiteError``. Handlers not yet implemented raise ``NotImplementedError``.
"""

from rmr.paths import step_output_path
from rmr.sources import scopus

ORIGINS = ["scopus", "google", "github", "pwc"]

STEPS = {
    1: "initial complete search",
    2: "title screening",
    3: "abstract & keywords screening",
    4: "full-text screening",
}


class PrerequisiteError(Exception):
    """Raised when a step is invoked before its predecessor ran for that origin."""


# (origin, step) -> handler. Only Scopus step 1 is implemented so far.
_HANDLERS = {
    ("scopus", 1): scopus.step1_initial_search,
}


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


def run(origin: str, step: int):
    handler = _HANDLERS.get((origin, step))
    if handler is None:
        raise NotImplementedError(
            f"step {step} ('{STEPS[step]}') for origin '{origin}' is not implemented yet"
        )
    return handler()
