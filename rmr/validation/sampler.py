"""Draw the reproducible stratified sample and write the blind labelling sheets.

For each origin the screened pool is split into the LLM ``include`` and ``exclude`` strata:
- the exclude stratum is taken in full (census) so recall is exact;
- the include stratum is randomly sampled (proportional allocation across origins).

The gold pool (sampled includes + all excludes) is then split between two raters:
- step 2 (titles are cheap): both raters label the whole pool (full double-labelling);
- step 3 (abstracts are costly): both label a stratified overlap subset, and the rest is
  split between them.

Sheets are blind: they never contain the LLM decision or the stratum, and their row order is
shuffled. The ``key.json`` (kept aside, not given to raters) records the LLM decision,
stratum and rater assignment for scoring.
"""

import csv
import json
import random
from datetime import datetime, timezone

from rmr.paths import (PROJECT_ROOT, ensure_parent, full_path, step_output_path,
                       validation_dir)
from rmr.screening.abstract import read_abstract
from rmr.validation import stats

ORIGINS = ["scopus", "google", "github", "hf"]
DEFAULT_MARGIN = 0.08          # +/- for the precision estimate (drives include-sample size)
DEFAULT_OVERLAP = 120          # step-3/4 items both raters label (inter-rater reliability)
MIN_INCLUDE_PER_ORIGIN = 8     # floor so small origins are still represented


def _extra_fields(step: int) -> list[str]:
    """Columns shown to raters beyond id/origin/title, by step."""
    if step == 3:
        return ["abstract", "keywords"]  # the abstract screening reads these
    if step == 4:
        return ["link", "source"]        # full-text review: the rater opens the source file
    return []


def _fulltext_source(origin: str, item_id: str) -> str:
    """Repo-relative path to the full text a step-4 rater should read."""
    return str(full_path(origin, item_id).relative_to(PROJECT_ROOT))


def _load(origin: str, step: int) -> list[dict]:
    """Return per-record dicts (id, origin, llm_decision, plus the step's display fields)."""
    path = step_output_path(origin, step)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = []
    for record in data.get("records", []):
        base = {"id": record["id"], "origin": origin,
                "title": "", "abstract": "", "keywords": "", "link": "", "source": ""}
        if step == 2:
            decision = record.get("decision")
            if decision not in ("include", "exclude"):
                continue
            base.update(llm_decision=decision, title=record.get("title", ""))
        else:
            if record.get("status") != "screened":
                continue
            decision = (record.get("screening") or {}).get("decision")
            if decision not in ("include", "exclude"):
                continue
            d = record.get("data", {})
            base.update(llm_decision=decision, title=d.get("title", ""), link=d.get("link", ""))
            if step == 3:  # captured content now lives in content/abstract/<id>.json
                cap = read_abstract(origin, record["id"])
                base["title"] = base["title"] or cap.get("title", "")
                base["abstract"] = cap.get("abstract") or cap.get("summary") or ""
                base["keywords"] = ", ".join(cap.get("keywords", []) or [])
            else:  # step 4: point the rater at the full-text file
                base["source"] = _fulltext_source(origin, record["id"])
        items.append(base)
    return items


def _allocate_includes(by_origin_includes: dict[str, list], total_n: int, rng) -> list[dict]:
    """Proportional allocation of the include sample across origins, then random draw."""
    populations = {o: len(v) for o, v in by_origin_includes.items() if v}
    grand = sum(populations.values())
    if grand == 0:
        return []
    sampled = []
    for origin, items in by_origin_includes.items():
        pop = len(items)
        if pop == 0:
            continue
        share = round(total_n * pop / grand)
        n = min(pop, max(MIN_INCLUDE_PER_ORIGIN, share))
        sampled.extend(rng.sample(items, n))
    return sampled


def build_sample(step: int, seed: int = 42, margin: float = DEFAULT_MARGIN,
                 overlap: int = DEFAULT_OVERLAP) -> dict:
    rng = random.Random(seed)

    includes_by_origin, excludes, populations = {}, [], {}
    for origin in ORIGINS:
        items = _load(origin, step)
        if not items:
            continue
        inc = [i for i in items if i["llm_decision"] == "include"]
        exc = [i for i in items if i["llm_decision"] == "exclude"]
        includes_by_origin[origin] = inc
        excludes.extend(exc)
        populations[origin] = {"include": len(inc), "exclude": len(exc)}

    total_includes = sum(len(v) for v in includes_by_origin.values())
    target = stats.sample_size(total_includes, margin=margin)
    sampled_includes = _allocate_includes(includes_by_origin, target, rng)

    for item in sampled_includes:
        item["stratum"] = "include"
    for item in excludes:
        item["stratum"] = "exclude"
    gold = sampled_includes + excludes  # excludes are censused

    # Rater assignment.
    if step == 2:
        for item in gold:
            item["assigned_to"] = "both"
    else:
        by_stratum = {"include": [i for i in gold if i["stratum"] == "include"],
                      "exclude": [i for i in gold if i["stratum"] == "exclude"]}
        overlap_ids = set()
        for stratum, items in by_stratum.items():
            k = min(len(items), round(overlap * len(items) / len(gold)))
            overlap_ids.update(i["id"] for i in rng.sample(items, k))
        rest = [i for i in gold if i["id"] not in overlap_ids]
        rng.shuffle(rest)
        for i, item in enumerate(gold):
            if item["id"] in overlap_ids:
                item["assigned_to"] = "both"
        for i, item in enumerate(rest):
            item["assigned_to"] = "A" if i % 2 == 0 else "B"

    _write_outputs(step, gold, seed, margin, overlap, target, populations, rng)
    return {"step": step, "gold": len(gold), "includes_sampled": len(sampled_includes),
            "excludes_census": len(excludes), "target_include_sample": target}


def _sheet_rows(step: int, items: list[dict], rng) -> list[dict]:
    rows = list(items)
    rng.shuffle(rows)  # hide any stratum ordering
    out = []
    for item in rows:
        row = {"id": item["id"], "origin": item["origin"], "title": item["title"]}
        for field in _extra_fields(step):
            row[field] = item.get(field, "")
        row["human_decision"] = ""  # rater fills: include | exclude
        row["human_note"] = ""
        out.append(row)
    return out


def _write_csv(path, rows: list[dict], fields: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_outputs(step, gold, seed, margin, overlap, target, populations, rng) -> None:
    out_dir = validation_dir(step)
    fields = ["id", "origin", "title"] + _extra_fields(step) + ["human_decision", "human_note"]

    for rater in ("A", "B"):
        assigned = [i for i in gold if i["assigned_to"] in ("both", rater)]
        _write_csv(out_dir / f"rater-{rater}.csv", _sheet_rows(step, assigned, rng), fields)

    key = {
        "step": step,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "precision_margin": margin,
        "overlap_target": "all" if step == 2 else overlap,
        "include_sample_target": target,
        "populations": populations,
        "items": [{"id": i["id"], "origin": i["origin"], "stratum": i["stratum"],
                   "llm_decision": i["llm_decision"], "assigned_to": i["assigned_to"]}
                  for i in gold],
    }
    key_path = out_dir / "key.json"
    ensure_parent(key_path)
    key_path.write_text(json.dumps(key, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {
        "gold_total": len(gold),
        "include_sampled": sum(1 for i in gold if i["stratum"] == "include"),
        "exclude_census": sum(1 for i in gold if i["stratum"] == "exclude"),
        "both": sum(1 for i in gold if i["assigned_to"] == "both"),
        "only_A": sum(1 for i in gold if i["assigned_to"] == "A"),
        "only_B": sum(1 for i in gold if i["assigned_to"] == "B"),
    }
    print(f"[validate] step {step}: {counts}")
    print(f"[validate] wrote sheets and key to {out_dir}")
