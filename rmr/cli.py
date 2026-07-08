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
        "--origin", required=True, choices=ORIGINS,
        help="Source to process: " + ", ".join(ORIGINS) + ".",
    )
    parser.add_argument(
        "--step", required=True, type=int, choices=list(STEPS),
        help="1 initial complete search, 2 title, 3 abstract & keywords, 4 full text.",
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
    try:
        steps.check_prerequisite(args.origin, args.step)
        steps.run(args.origin, args.step, args.substep)
    except (PrerequisiteError, NotImplementedError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
