"""Command-line interface: parse and validate arguments, then dispatch a step."""

import argparse
import sys

from rmr import steps
from rmr.steps import ORIGINS, STEPS, SUBSTEPS, PrerequisiteError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rmr",
        description="Rapid Multivocal Review pipeline: run search and filtering per origin and step.",
    )
    parser.add_argument(
        "--origin", choices=ORIGINS,
        help="Source to process: " + ", ".join(ORIGINS) + ". Required for steps 1-4; "
             "ignored for steps 5-7 (which aggregate all origins).",
    )
    parser.add_argument(
        "--step", required=True, type=int, choices=list(STEPS),
        help="1 initial complete search, 2 title, 3 abstract & keywords, 4 full text, "
             "5 export blind human-review spreadsheets, 6 generate blind tie-break "
             "spreadsheets, 7 compute screening metrics (steps 5-7 cover all origins).",
    )
    parser.add_argument(
        "--substep", choices=SUBSTEPS, default=None,
        help="Step 3 only: run a single phase (" + ", ".join(SUBSTEPS) + "). Omit to run all.",
    )
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.substep and args.step != 3:
        parser.error("--substep is only valid with --step 3")
    if args.step not in (5, 6, 7) and not args.origin:
        parser.error("--origin is required for steps 1-4")
    try:
        _dispatch(args)
    except (PrerequisiteError, NotImplementedError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


def _dispatch(args) -> None:
    # local imports keep the openpyxl dependency (steps 5-7) out of steps 1-4
    if args.step == 5:
        from rmr import review
        review.export_review_sheets()
        return
    if args.step == 6:
        from rmr import review
        review.export_tiebreak_sheets()
        return
    if args.step == 7:
        from rmr import metrics
        metrics.export_metrics()
        return
    steps.check_prerequisite(args.origin, args.step)
    steps.run(args.origin, args.step, args.substep)
