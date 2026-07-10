"""Step 7: screening-reliability metrics from the human reviews.

Gold standard (census + adjudication):
- LLM == reviewer 1  -> gold = that decision (two independents agree).
- LLM != reviewer 1  -> gold = reviewer 2 (the step-6 tie-break).
- reviewer 1 left it blank, or a conflict has no reviewer 2 yet -> pending, excluded from the
  metrics (its count is reported).

The positive class is ``include``. Per origin and pooled, it reports the LLM-vs-gold confusion
matrix (TP/FP/FN/TN); precision, recall, F1, accuracy; and the LLM-vs-reviewer-1 percent
agreement with the conflict/adjudication tallies. For ``step-4-answers`` it reports the
validation rate (final agreement 'yes' after adjudication). Writes metrics.json and prints a
summary. Reads files only; no LLM calls.
"""

import json
from datetime import datetime, timezone

from rmr import config
from rmr.paths import ensure_parent
from rmr.review import (INCLUDE_EXCLUDE, ORIGINS, YES_NO, _records, _sheet_column,
                        review_dir)
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
    r1 = _sheet_column(review / f"step-{step}-review.xlsx", "decision") or {}
    r2 = _sheet_column(review / "tiebreak" / f"step-{step}-tiebreak.xlsx", "decision") or {}

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


def _answers_step(review) -> dict | None:
    """Validation rate of the research-answer extraction: fraction whose final agreement is
    'yes' after adjudication (reviewer 1 'yes', or reviewer 1 'no' overturned by reviewer 2)."""
    r1 = _sheet_column(review / "step-4-answers-review.xlsx", "Agreement")
    if r1 is None:
        return None
    r2 = _sheet_column(review / "tiebreak" / "step-4-answers-tiebreak.xlsx", "Agreement") or {}
    reviewed = final_yes = r1_yes = r1_no = overturned = confirmed = 0
    pending_review = pending_adjudication = 0
    for rid, value in r1.items():
        if value not in YES_NO:
            pending_review += 1
            continue
        reviewed += 1
        if value == "yes":
            r1_yes += 1
            final_yes += 1
        else:
            r1_no += 1
            r2_v = r2.get(rid, "")
            if r2_v not in YES_NO:
                pending_adjudication += 1
            elif r2_v == "yes":
                overturned += 1
                final_yes += 1
            else:
                confirmed += 1
    finalized = reviewed - pending_adjudication
    return {
        "reviewed": reviewed, "finalized": finalized, "validated": final_yes,
        "validation_rate": final_yes / finalized if finalized else 0.0,
        "reviewer1_yes": r1_yes, "reviewer1_no": r1_no,
        "adjudicated_overturned": overturned, "adjudicated_confirmed": confirmed,
        "pending_review": pending_review, "pending_adjudication": pending_adjudication,
    }


def _pct(x: float) -> str:
    return f"{x * 100:5.1f}%"


def _print_summary(result: dict) -> None:
    print("\n=== Screening reliability (LLM vs human gold) ===")
    for step in SCREENING_STEPS:
        data = result["screening"][str(step)]
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

    ans = result.get("answers")
    print("\n=== Research-answer extraction ===")
    if not ans:
        print("  (no answers review sheet)")
    else:
        print(f"  validation_rate={_pct(ans['validation_rate'])} "
              f"(validated={ans['validated']}/{ans['finalized']}); "
              f"R1 yes/no={ans['reviewer1_yes']}/{ans['reviewer1_no']}; "
              f"R2 overturned={ans['adjudicated_overturned']} confirmed={ans['adjudicated_confirmed']}; "
              f"pending={ans['pending_review'] + ans['pending_adjudication']}")


REVIEWER_STAMPS = ("reviewer a", "reviewer b")


def _check_review(review, name: str, decision_col: str, expected: tuple) -> list[str]:
    """Issue(s) if a review sheet is missing, has any unfilled decision cell, or any row
    without a Reviewer stamp."""
    decisions = _sheet_column(review / name, decision_col)
    if decisions is None:
        return [f"{name}: missing"]
    issues = []
    blanks = [rid for rid, value in decisions.items() if value not in expected]
    if blanks:
        issues.append(f"{name}: {len(blanks)} of {len(decisions)} decisions not filled")
    reviewers = _sheet_column(review / name, "Reviewer") or {}
    unstamped = [rid for rid in decisions if reviewers.get(rid, "") not in REVIEWER_STAMPS]
    if unstamped:
        issues.append(f"{name}: {len(unstamped)} of {len(decisions)} rows not stamped (Reviewer)")
    return issues


def _check_tiebreak(review, name: str, decision_col: str, conflicts: set,
                    expected: tuple) -> list[str]:
    """Issue(s) if any conflict lacks a reviewer-2 (tie-break) decision."""
    if not conflicts:
        return []
    tb = _sheet_column(review / "tiebreak" / name, decision_col) or {}
    missing = [rid for rid in conflicts if tb.get(rid, "") not in expected]
    if missing:
        return [f"tiebreak/{name}: {len(missing)} of {len(conflicts)} conflicts not resolved"]
    return []


def _incomplete(review) -> list[str]:
    """Every review AND tie-break sheet must be fully filled (decisions and Reviewer stamps)
    before metrics are computed. Returns a list of issues (empty when everything is complete)."""
    issues = []
    for step in SCREENING_STEPS:
        issues += _check_review(review, f"step-{step}-review.xlsx", "decision", INCLUDE_EXCLUDE)
    issues += _check_review(review, "step-4-answers-review.xlsx", "Agreement", YES_NO)

    for step in SCREENING_STEPS:
        r1 = _sheet_column(review / f"step-{step}-review.xlsx", "decision")
        if r1 is None:
            continue  # already reported as missing above
        llm = {rid: d for _, rid, d in _llm_by_origin(step)}
        conflicts = {rid for rid, v in r1.items()
                     if v in INCLUDE_EXCLUDE and llm.get(rid) and llm[rid] != v}
        issues += _check_tiebreak(review, f"step-{step}-tiebreak.xlsx", "decision",
                                  conflicts, INCLUDE_EXCLUDE)
    ans = _sheet_column(review / "step-4-answers-review.xlsx", "Agreement")
    if ans is not None:
        conflicts = {rid for rid, v in ans.items() if v == "no"}
        issues += _check_tiebreak(review, "step-4-answers-tiebreak.xlsx", "Agreement",
                                  conflicts, YES_NO)
    return issues


def export_metrics() -> dict:
    """Compute the screening metrics for the current experiment; write metrics.json and print.

    Refuses to run unless every review and tie-break sheet is fully filled (no partial data):
    otherwise it raises with the list of what is still missing.
    """
    review = review_dir()
    issues = _incomplete(review)
    if issues:
        raise RuntimeError(
            "step 7 requires every review and tie-break sheet to be fully filled; "
            "the following are incomplete:\n  - " + "\n  - ".join(issues)
            + f"\n(sheets under {review}; fill reviewer 1, run step 6, fill reviewer 2, retry)"
        )
    result = {
        "model_experiment": config.model_experiment(),
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "screening": {str(step): _screening_step(step, review) for step in SCREENING_STEPS},
        "answers": _answers_step(review),
    }
    path = review / "metrics" / "metrics.json"
    ensure_parent(path)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    _print_summary(result)
    print(f"\n[metrics] wrote {path}")
    return result
