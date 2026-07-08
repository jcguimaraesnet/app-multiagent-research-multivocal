"""CLI for screening validation (steps 2 and 3).

Usage:
  uv run python validate.py sample --step <2|3> [--seed 42] [--margin 0.08] [--overlap 120]
  uv run python validate.py score  --step <2|3>

`sample` draws the reproducible stratified sample and writes the blind rater sheets
(rater-A.csv, rater-B.csv) plus key.json under data/validation/step-<n>/.
`score` reads the filled sheets (+ optional adjudication.csv) and reports the metrics.
"""

import argparse

from rmr.validation import sampler, scorer


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="validate", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("sample", help="draw the stratified sample and write blind sheets")
    s.add_argument("--step", type=int, choices=[2, 3, 4], required=True)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--margin", type=float, default=sampler.DEFAULT_MARGIN,
                   help="precision margin of error (drives the include-sample size)")
    s.add_argument("--overlap", type=int, default=sampler.DEFAULT_OVERLAP,
                   help="step-3/4 items both raters label (inter-rater reliability)")

    c = sub.add_parser("score", help="read labels and compute metrics")
    c.add_argument("--step", type=int, choices=[2, 3, 4], required=True)

    args = parser.parse_args(argv)
    if args.command == "sample":
        sampler.build_sample(args.step, seed=args.seed, margin=args.margin, overlap=args.overlap)
    else:
        scorer.score(args.step)


if __name__ == "__main__":
    main()
