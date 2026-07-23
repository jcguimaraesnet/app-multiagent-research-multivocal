"""Step 7: screening-reliability metrics from the human reviews.

Everything is read from the reviewers' filled workbook of each step
(``step-<n>-review-reviewed.xlsx``), whose ``Review 1`` column holds the first reviewer's
verdict on every row and whose ``Review 2`` column holds the adjudication of the rows where
reviewer 1 differed from the model.

Gold standard (census + adjudication):
- LLM == reviewer 1  -> gold = that decision (two independents agree).
- LLM != reviewer 1  -> gold = reviewer 2 (the adjudication).
- reviewer 1 left it blank, or a conflict has no reviewer 2 yet -> pending, excluded from the
  metrics (its count is reported).

The positive class is ``include``. Per origin and pooled, it reports the LLM-vs-gold confusion
matrix (TP/FP/FN/TN); precision, recall, F1, accuracy; and the LLM-vs-reviewer-1 percent
agreement with the conflict/adjudication tallies. Writes metrics.json and prints a summary.
Reads files only; no LLM calls.
"""

import json
from datetime import datetime, timezone

from rmr import config
from rmr.paths import ensure_parent
from rmr.review import (INCLUDE_EXCLUDE, ORIGINS, R1_COL, R2_COL, REVIEWED_SHEETS, _records,
                        first_pass_column, review_dir, reviewed_column)
from rmr.validation.stats import percent_agreement

SCREENING_STEPS = [2, 3, 4]


def _llm_by_origin(step: int) -> list[tuple[str, str, str]]:
    """[(origin, id, 'include'|'exclude')] for every record the LLM screened at ``step``."""
    rows = []
    for origin in ORIGINS:
        records = _records(origin, step)
        if records is None:
            continue
        for record in records:
            rid = record.get("id")
            decision = (record.get("decision") if step == 2
                        else (record.get("screening") or {}).get("decision"))
            if rid and decision:
                rows.append((origin, str(rid), decision.strip().lower()))
    return rows


def _metrics_from_counts(tp: int, fp: int, fn: int, tn: int, pairs: list) -> dict:
    """Precision/recall/F1/accuracy (positive = include) plus LLM-vs-reviewer-1 agreement,
    from a confusion matrix and the (llm, reviewer1) label pairs."""
    n = tp + fp + fn + tn
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {
        "n": n, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        "accuracy": (tp + tn) / n if n else 0.0,
        "agreement_pct": percent_agreement(pairs),
    }


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0


def _screening_step(step: int, review) -> dict:
    """Metrics for one screening step, per origin and pooled."""
    r1 = first_pass_column(review, step) or {}
    r2 = reviewed_column(review, step, R2_COL) or {}

    origins: dict[str, dict] = {}
    pending_review = pending_adjudication = 0
    sided_with_llm = sided_with_reviewer1 = 0

    def bucket(origin: str) -> dict:
        return origins.setdefault(origin, {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "pairs": []})

    for origin, rid, llm_d in _llm_by_origin(step):
        r1_d = r1.get(rid, "")
        if r1_d not in INCLUDE_EXCLUDE:
            pending_review += 1
            continue
        entry = bucket(origin)
        entry["pairs"].append((llm_d, r1_d))  # LLM-vs-reviewer-1 pair (defined for all reviewed)
        if llm_d == r1_d:
            gold = r1_d
        else:
            r2_d = r2.get(rid, "")
            if r2_d not in INCLUDE_EXCLUDE:
                pending_adjudication += 1
                continue  # conflict not yet adjudicated: no gold, skip the confusion matrix
            gold = r2_d
            if r2_d == llm_d:
                sided_with_llm += 1
            else:
                sided_with_reviewer1 += 1
        cell = ("tp" if gold == "include" else "fp") if llm_d == "include" else \
               ("fn" if gold == "include" else "tn")
        entry[cell] += 1

    pooled_pairs = [pair for e in origins.values() for pair in e["pairs"]]
    conflicts = sum(1 for a, b in pooled_pairs if a != b)
    by_origin = {o: _metrics_from_counts(e["tp"], e["fp"], e["fn"], e["tn"], e["pairs"])
                 for o, e in origins.items()}
    totals = {k: sum(e[k] for e in origins.values()) for k in ("tp", "fp", "fn", "tn")}
    return {
        "step": step,
        "reviewed": len(pooled_pairs),
        "pending_review": pending_review,
        "pending_adjudication": pending_adjudication,
        "conflicts": conflicts,
        "conflict_rate": conflicts / len(pooled_pairs) if pooled_pairs else 0.0,
        "adjudication": {"resolved": sided_with_llm + sided_with_reviewer1,
                         "sided_with_llm": sided_with_llm,
                         "sided_with_reviewer1": sided_with_reviewer1},
        "by_origin": by_origin,
        "pooled": _metrics_from_counts(totals["tp"], totals["fp"], totals["fn"],
                                       totals["tn"], pooled_pairs),
    }


def _pct(x: float) -> str:
    return f"{x * 100:5.1f}%"


def _print_summary(result: dict) -> None:
    print("\n=== Screening reliability (LLM vs human gold) ===")
    for step in SCREENING_STEPS:
        data = result["screening"].get(str(step))
        if data is None:
            continue
        p = data["pooled"]
        print(f"\nStep {step}: reviewed={data['reviewed']} "
              f"conflicts={data['conflicts']} ({_pct(data['conflict_rate']).strip()}) "
              f"pending_review={data['pending_review']} "
              f"pending_adjud={data['pending_adjudication']}")
        if p["n"] == 0:
            print("  (no adjudicated items yet)")
            continue
        print(f"  precision={_pct(p['precision'])}  recall={_pct(p['recall'])}  "
              f"F1={_pct(p['f1'])}  accuracy={_pct(p['accuracy'])}")
        print(f"  agreement={_pct(p['agreement_pct'])}  "
              f"(TP={p['tp']} FP={p['fp']} FN={p['fn']} TN={p['tn']})")

    skipped = result.get("skipped") or {}
    if skipped:
        print("\n=== Not scored yet (review still incomplete) ===")
        for key, issues in skipped.items():
            for issue in issues:
                print(f"  {key}: {issue}")



def _check_review(label: str, r1: dict | None, expected: tuple) -> list[str]:
    """Issue(s) if a reviewed sheet is missing or leaves any ``Review 1`` cell unfilled."""
    if r1 is None:
        return [f"{label}: missing"]
    if not r1:
        return [f"{label}: no '{R1_COL}' column"]
    blanks = [rid for rid, value in r1.items() if value not in expected]
    if blanks:
        return [f"{label}: {len(blanks)} of {len(r1)} '{R1_COL}' cells not filled"]
    return []


def _check_adjudication(label: str, r2: dict, conflicts: set, expected: tuple) -> list[str]:
    """Issue(s) if any conflict lacks a reviewer-2 (``Review 2``) decision."""
    missing = [rid for rid in conflicts if r2.get(rid, "") not in expected]
    if missing:
        return [f"{label}: {len(missing)} of {len(conflicts)} conflicts have no '{R2_COL}'"]
    return []


def _step_issues(review, step: int) -> list[str]:
    """Completeness issues of one screening step, empty when the step can be scored:
    every screened record has a ``Review 1`` verdict, and ``Review 2`` is filled on every
    conflict."""
    label = REVIEWED_SHEETS[step]
    r1 = first_pass_column(review, step)
    issues = _check_review(label, r1, INCLUDE_EXCLUDE)
    if issues:
        return issues
    llm = {rid: d for _, rid, d in _llm_by_origin(step)}
    # Coverage: every record the model screened must have a verdict, so a survivor that never
    # made it onto a sheet (e.g. a late residual) is caught instead of being silently dropped.
    uncovered = sorted(rid for rid in llm if r1.get(rid) not in INCLUDE_EXCLUDE)
    if uncovered:
        return [f"{label}: {len(uncovered)} screened record(s) have no '{R1_COL}' verdict "
                f"({', '.join(uncovered[:8])})"]
    conflicts = {rid for rid, value in r1.items()
                 if value in INCLUDE_EXCLUDE and llm.get(rid) and llm[rid] != value}
    r2 = reviewed_column(review, step, R2_COL) or {}
    return _check_adjudication(label, r2, conflicts, INCLUDE_EXCLUDE)


def export_metrics() -> dict:
    """Compute the screening metrics for the current experiment; write metrics.json and print.

    Completeness is enforced PER STEP: a step is scored only when its sheet is fully filled
    (``Review 1`` on every row, ``Review 2`` on every conflict), so a step still under review
    is reported as skipped instead of blocking the ones already finished. It raises only when
    nothing at all can be scored.
    """
    review = review_dir()
    screening, skipped = {}, {}
    for step in SCREENING_STEPS:
        issues = _step_issues(review, step)
        if issues:
            skipped[str(step)] = issues
        else:
            screening[str(step)] = _screening_step(step, review)

    if not screening:
        raise RuntimeError(
            "no reviewed sheet is complete enough to score; the following are incomplete:\n  - "
            + "\n  - ".join(issue for issues in skipped.values() for issue in issues)
            + f"\n(sheets under {review}; fill '{R1_COL}', run step 6 to list the conflicts, "
            f"fill '{R2_COL}' on them, then retry)"
        )

    result = {
        "model_experiment": config.model_experiment(),
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "screening": screening,
        "skipped": skipped,
    }
    path = review / "metrics" / "metrics.json"
    ensure_parent(path)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    _print_summary(result)
    print(f"\n[metrics] wrote {path}")
    return result
