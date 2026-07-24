"""Step 8: reconcile a screening step's human review back into the pipeline.

The reviewers filled one sheet per screening step with three decision columns:
``Review 1`` (the first reviewer, who judges every row), ``Review 2`` (the second
reviewer, who adjudicates only the rows where ``Review 1`` differs from the LLM) and
``Finale`` (the consolidated verdict). This step reads ``Finale`` and stores it on every
screened record as ``human_decision``, leaving the LLM's own ``decision`` untouched so the
metrics keep comparing model against human. It also writes the final human tally onto the root
of each step's JSON (``human_included``/``human_excluded``, next to the LLM's own
``included``/``excluded``), which is what the PRISMA flow reports.

It also reports the *residuals*: records the LLM excluded but the humans included. Those
must still travel to the next screening step, which selects its survivors by
``human_decision`` when present (see ``rmr.screening.abstract._survivors``).

Reads and writes files only; no LLM calls.
"""

import json
from datetime import datetime, timezone

from rmr import config
from rmr.paths import ensure_parent, review_dir, step_output_path
from rmr.review import (FINAL_COL, INCLUDE_EXCLUDE, ORIGINS, R2_COL, REVIEWED_SHEETS,
                        first_pass_column, reviewed_column)

LLM_COL = "llm_decision"  # the model's verdict, carried in the sheet purely as a reference


def _insert_after(doc: dict, anchor: str, extra: dict) -> dict:
    """Return ``doc`` with ``extra``'s keys inserted right after ``anchor`` (kept adjacent to
    the LLM's own tally). Existing keys are overwritten in place; if ``anchor`` is absent the
    extras are appended. Preserves insertion order for a readable JSON file."""
    if anchor not in doc:
        return {**doc, **extra}
    rebuilt = {}
    for key, value in doc.items():
        if key in extra:
            continue  # re-placed below, next to the anchor
        rebuilt[key] = value
        if key == anchor:
            rebuilt.update(extra)
    return rebuilt


def _llm_decision(record: dict, step: int) -> str:
    """The LLM verdict as the step stores it: top level at step 2, nested afterwards."""
    value = (record.get("decision") if step == 2
             else (record.get("screening") or {}).get("decision"))
    return (value or "").strip().lower()


def _title(record: dict) -> str:
    return record.get("title") or record.get("data", {}).get("title", "")


def _consistency_warnings(llm: dict, r1: dict, r2: dict, final: dict) -> list[str]:
    """Sheet-level warnings (never fatal): rows without a final verdict, and rows whose
    ``Finale`` does not follow the adjudication rule (reviewer 1 when the LLM agreed with
    them, otherwise reviewer 2)."""
    issues = []
    blank = [rid for rid, value in final.items() if value not in INCLUDE_EXCLUDE]
    if blank:
        issues.append(f"{len(blank)} row(s) without a '{FINAL_COL}' decision")

    broken = []
    for rid, verdict in final.items():
        first, tie, model = r1.get(rid, ""), r2.get(rid, ""), llm.get(rid, "")
        if verdict not in INCLUDE_EXCLUDE or first not in INCLUDE_EXCLUDE or not model:
            continue
        if model == first:
            expected = first
        elif tie in INCLUDE_EXCLUDE:
            expected = tie
        else:
            continue  # a conflict with no tie-break yet: nothing to check
        if verdict != expected:
            broken.append(rid)
    if broken:
        issues.append(f"{len(broken)} row(s) whose '{FINAL_COL}' differs from the "
                      f"reviewer-1/reviewer-2 rule ({', '.join(broken[:5])})")
    return issues


def reconcile_step(step: int) -> dict | None:
    """Apply the reviewed sheet of one screening step. Returns None when it is absent."""
    review = review_dir()
    name = REVIEWED_SHEETS[step]
    final = reviewed_column(review, step, FINAL_COL)
    if final is None:
        print(f"[reconcile] step {step}: {name} not found, skipped")
        return None
    if not final:
        raise RuntimeError(f"{review / name} has no '{FINAL_COL}' column")

    llm_sheet = reviewed_column(review, step, LLM_COL) or {}
    r1 = first_pass_column(review, step) or {}
    r2 = reviewed_column(review, step, R2_COL) or {}
    for issue in _consistency_warnings(llm_sheet, r1, r2, final):
        print(f"[reconcile] step {step} warning: {issue}")

    residuals, by_origin, matched = [], {}, set()
    for origin in ORIGINS:
        doc_path = step_output_path(origin, step)
        if not doc_path.exists():
            print(f"[reconcile] step {step}: no output for '{origin}', skipped")
            continue
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        records = doc.get("records", [])

        reviewed = included = recovered = dropped = 0
        for record in records:
            rid = str(record.get("id", ""))
            verdict = final.get(rid, "")
            if verdict not in INCLUDE_EXCLUDE:
                continue  # not reviewed: leave the record exactly as the LLM left it
            matched.add(rid)
            record["human_decision"] = verdict
            reviewed += 1
            model = _llm_decision(record, step)
            if verdict == "include":
                included += 1
            if model == "exclude" and verdict == "include":
                recovered += 1
                residuals.append({"id": rid, "origin": origin, "title": _title(record),
                                  "llm_decision": model, "human_decision": verdict})
            elif model == "include" and verdict == "exclude":
                dropped += 1

        human_excluded = reviewed - included
        # Root-level final tally, mirroring the LLM's own `included`/`excluded`: place the
        # human pair right after it so a reader can compare model vs. human side by side.
        doc = _insert_after(doc, "excluded",
                            {"human_included": included, "human_excluded": human_excluded})
        doc["human_review"] = {
            "sheet": REVIEWED_SHEETS[step],
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "reviewed": reviewed,
            "human_included": included, "human_excluded": human_excluded,
            "recovered_from_exclude": recovered, "dropped_from_include": dropped,
        }
        doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        by_origin[origin] = {"reviewed": reviewed, "human_included": included,
                             "recovered_from_exclude": recovered,
                             "dropped_from_include": dropped}
        print(f"[reconcile] {origin} step {step}: {reviewed} reviewed, "
              f"{included} included by humans (+{recovered} recovered, -{dropped} dropped)")

    orphans = sorted(rid for rid, value in final.items()
                     if value in INCLUDE_EXCLUDE and rid not in matched)
    if orphans:
        print(f"[reconcile] step {step} warning: {len(orphans)} sheet row(s) match no record "
              f"({', '.join(orphans[:5])})")

    result = {
        "step": step,
        "model_experiment": config.model_experiment(),
        "sheet": REVIEWED_SHEETS[step],
        "reconciled_at": datetime.now(timezone.utc).isoformat(),
        "by_origin": by_origin,
        "totals": {key: sum(o[key] for o in by_origin.values())
                   for key in ("reviewed", "human_included",
                               "recovered_from_exclude", "dropped_from_include")},
        "unmatched_sheet_rows": orphans,
        "residuals": residuals,
    }
    out = review / "residuals" / f"step-{step}-residuals.json"
    ensure_parent(out)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    totals = result["totals"]
    print(f"[reconcile] step {step}: {totals['human_included']} included by humans "
          f"({totals['recovered_from_exclude']} residuals recovered from the LLM's excludes, "
          f"{totals['dropped_from_include']} dropped from its includes)")
    if residuals:
        print(f"[reconcile] step {step} residuals -> "
              f"{', '.join(r['id'] for r in residuals)}")
    print(f"[reconcile] wrote {out}")
    return result


def reconcile() -> dict:
    """Reconcile every screening step whose reviewed sheet is present (step 8)."""
    results = {}
    for step in sorted(REVIEWED_SHEETS):
        outcome = reconcile_step(step)
        if outcome is not None:
            results[str(step)] = outcome
    if not results:
        raise RuntimeError(
            "no reviewed sheet found in " + str(review_dir())
            + "; expected one of: " + ", ".join(REVIEWED_SHEETS.values())
        )
    return results
