"""Read the two raters' labels, build the gold standard, and compute the metrics.

Outputs:
- inter-rater reliability on the overlap (percent agreement, Cohen's kappa, Gwet's AC1);
- precision / recall / F1 of the LLM screening vs the gold, per origin and pooled, with
  95% confidence intervals (precision from the include sample; recall from the exclude
  census, propagated through the precision interval).

Overlap disagreements need adjudication: if ``adjudication.csv`` (columns id,
adjudicated_decision) is absent, a template is written and those items are left unresolved.
"""

import csv
import json

from rmr.paths import ensure_parent, validation_dir
from rmr.validation import stats

VALID = {"include", "exclude"}


def _read_labels(path) -> dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            decision = (row.get("human_decision") or "").strip().lower()
            if decision in VALID:
                out[row["id"]] = decision
    return out


def _build_gold(items, labels_a, labels_b, adjudication):
    """Return (gold: {id: decision}, overlap_pairs, unresolved, disagreements)."""
    gold, pairs, unresolved, disagreements = {}, [], [], []
    for item in items:
        rid, assigned = item["id"], item["assigned_to"]
        a, b = labels_a.get(rid), labels_b.get(rid)
        if assigned == "both":
            if a and b:
                pairs.append((a, b))
                if a == b:
                    gold[rid] = a
                elif rid in adjudication:
                    gold[rid] = adjudication[rid]
                    disagreements.append((rid, a, b, adjudication[rid]))
                else:
                    unresolved.append(rid)
                    disagreements.append((rid, a, b, ""))
            else:
                unresolved.append(rid)
        else:
            label = a if assigned == "A" else b
            if label:
                gold[rid] = label
            else:
                unresolved.append(rid)
    return gold, pairs, unresolved, disagreements


def _metrics_for(items, gold, origins):
    """Stratified precision/recall/F1 over the given origins (a subset, or all for pooled)."""
    inc = [i for i in items if i["stratum"] == "include" and i["origin"] in origins]
    exc = [i for i in items if i["stratum"] == "exclude" and i["origin"] in origins]
    inc_labelled = [i for i in inc if i["id"] in gold]
    exc_labelled = [i for i in exc if i["id"] in gold]
    tp_sample = sum(1 for i in inc_labelled if gold[i["id"]] == "include")
    false_neg = sum(1 for i in exc_labelled if gold[i["id"]] == "include")
    include_pop = sum(POP[o]["include"] for o in origins)
    exclude_pop = sum(POP[o]["exclude"] for o in origins)
    result = stats.stratified_metrics(tp_sample, len(inc_labelled), include_pop,
                                      false_neg, exclude_pop)
    result["exclude_labelled"] = len(exc_labelled)
    return result


POP: dict = {}  # populations from key.json, set in score()


def score(step: int) -> dict:
    out_dir = validation_dir(step)
    key = json.loads((out_dir / "key.json").read_text(encoding="utf-8"))
    global POP
    POP = key["populations"]
    items = key["items"]

    labels_a = _read_labels(out_dir / "rater-A.csv")
    labels_b = _read_labels(out_dir / "rater-B.csv")
    adjudication = _read_labels_adjudication(out_dir / "adjudication.csv")

    gold, pairs, unresolved, disagreements = _build_gold(items, labels_a, labels_b, adjudication)

    inter = {
        "overlap_n": len(pairs),
        "percent_agreement": stats.percent_agreement(pairs),
        "cohen_kappa": stats.cohen_kappa(pairs),
        "gwet_ac1": stats.gwet_ac1(pairs),
        "disagreements": len(pairs) - sum(1 for a, b in pairs if a == b),
    }

    origins = sorted({i["origin"] for i in items})
    per_origin = {o: _metrics_for(items, gold, [o]) for o in origins}
    pooled = _metrics_for(items, gold, origins)

    report = {"step": step, "gold_labelled": len(gold), "unresolved": len(unresolved),
              "inter_rater": inter, "pooled": pooled, "per_origin": per_origin}

    _maybe_write_adjudication_template(out_dir, items, disagreements, adjudication)
    (out_dir / "metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    _print_report(report, unresolved, adjudication)
    return report


def _read_labels_adjudication(path) -> dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            decision = (row.get("adjudicated_decision") or "").strip().lower()
            if decision in VALID:
                out[row["id"]] = decision
    return out


def _maybe_write_adjudication_template(out_dir, items, disagreements, adjudication) -> None:
    pending = [d for d in disagreements if not d[3]]
    if not pending or adjudication:
        return
    origin_by_id = {i["id"]: i["origin"] for i in items}
    path = out_dir / "adjudication-template.csv"
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "origin", "rater_A", "rater_B", "adjudicated_decision"])
        for rid, a, b, _ in pending:
            writer.writerow([rid, origin_by_id.get(rid, ""), a, b, ""])
    print(f"[validate] {len(pending)} overlap disagreements need adjudication -> {path}")
    print("[validate] fill 'adjudicated_decision', save as adjudication.csv, and re-run score")


def _fmt(m: dict) -> str:
    def ci(name):
        lo, hi = m[f"{name}_ci"]
        return f"{m[name]:.3f} [{lo:.3f}, {hi:.3f}]"
    return (f"P={ci('precision')}  R={ci('recall')}  F1={ci('f1')}  "
            f"(inc pop={m['include_pop']}, sample={m['include_sample']}, "
            f"FN={m['false_neg']}/{m['exclude_pop']} exc)")


def _print_report(report, unresolved, adjudication) -> None:
    print(f"\n=== Step {report['step']} validation ===")
    print(f"gold labelled: {report['gold_labelled']}  unresolved: {report['unresolved']}")
    i = report["inter_rater"]
    print(f"\nInter-rater (overlap n={i['overlap_n']}, disagreements={i['disagreements']}):")
    print(f"  percent agreement={i['percent_agreement']:.3f}  "
          f"Cohen kappa={i['cohen_kappa']:.3f}  Gwet AC1={i['gwet_ac1']:.3f}")
    print("\nScreening vs gold (95% CI):")
    print(f"  POOLED   {_fmt(report['pooled'])}")
    for origin, m in report["per_origin"].items():
        print(f"  {origin:8} {_fmt(m)}")
    if unresolved:
        print(f"\nNote: {len(unresolved)} items unresolved (missing labels or unadjudicated "
              "disagreements); excluded from the metrics above.")
