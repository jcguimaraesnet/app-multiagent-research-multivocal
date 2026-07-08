"""Step 3: abstract-level screening.

Single source of truth: data/<origin>/step-3.json. Each record has `id` and `status` at the
root, the scraped/source fields under `data`, and the screening result under `screening`.
The first thing step 3 does is build/load that manifest.

Status:
- Grey: pending -> scraped -> summarized -> screened. `data.summary` holds the summary.
- Academic: pending -> scraped -> screened (skips `summarized`, the Scopus gateway scrape
  already yields the abstract). `data.abstract` holds the abstract.
A scrape failure short-circuits to `screened` with an EC3 (unavailable) exclusion.

Screening applies IC1-IC5 and EC3/EC4/EC5. EC3 (content availability) is set by code; the
rest (IC1-IC5, EC4, EC5) are assessed by the Screener Agent, each with a verdict
(met/not_met/unclear) and a short note (empty when unclear). `decision` and `reason` are
derived from the criteria: exclude if any IC is `not_met` or any EC is `met`.

Substeps (see `--substep`), each acting only on records in the matching status:
- scrape:  grey -> content/<id>.md (status -> scraped); academic -> data.abstract (scraped).
- summary: grey only, condense the scraped page into data.summary (status -> summarized).
- screen:  per-criterion assessment + derived decision into `screening`.
"""

import json
from datetime import datetime, timezone
from typing import Literal

from agents import Agent, ModelSettings, Runner, set_tracing_disabled
from pydantic import BaseModel

from rmr.content import arxiv, scopus_gateway, scrape
from rmr.llm import openrouter_model
from rmr.paths import PROJECT_ROOT, content_path, ensure_parent, step_output_path

set_tracing_disabled(True)

SUMMARY_PROMPT = PROJECT_ROOT / "prompts" / "step3-summary.md"
HF_KEYWORDS_PROMPT = PROJECT_ROOT / "prompts" / "step3-hf-keywords.md"
SCREEN_PROMPT = PROJECT_ROOT / "prompts" / "step3-abstract-screening.md"
MAX_KEYWORDS = 5
SUBSTEPS = ["scrape", "summary", "screen"]

PENDING, SCRAPED, SUMMARIZED, SCREENED = "pending", "scraped", "summarized", "screened"

LLM_CRITERIA = ["IC1", "IC2", "IC3", "IC4", "IC5", "EC4", "EC5"]
CRITERIA_ORDER = ["IC1", "IC2", "IC3", "IC4", "IC5", "EC3", "EC4", "EC5"]


def _is_academic(origin: str) -> bool:
    return origin == "scopus"


def _statuses(origin: str) -> list[str]:
    if _is_academic(origin):
        return [PENDING, SCRAPED, SCREENED]
    return [PENDING, SCRAPED, SUMMARIZED, SCREENED]


def _ready_status(origin: str) -> str:
    return SCRAPED if _is_academic(origin) else SUMMARIZED


class SourceSummary(BaseModel):
    summary: str
    author: str = ""
    publication_date: str = ""
    keywords: list[str] = []


class KeywordsResult(BaseModel):
    keywords: list[str] = []


class ScreeningResult(BaseModel):
    IC1_verdict: Literal["met", "not_met", "unclear"]
    IC1_note: str = ""
    IC2_verdict: Literal["met", "not_met", "unclear"]
    IC2_note: str = ""
    IC3_verdict: Literal["met", "not_met", "unclear"]
    IC3_note: str = ""
    IC4_verdict: Literal["met", "not_met", "unclear"]
    IC4_note: str = ""
    IC5_verdict: Literal["met", "not_met", "unclear"]
    IC5_note: str = ""
    EC4_verdict: Literal["met", "not_met", "unclear"]
    EC4_note: str = ""
    EC5_verdict: Literal["met", "not_met", "unclear"]
    EC5_note: str = ""
    confidence: Literal["low", "medium", "high"]


def _criteria_from_result(result: ScreeningResult) -> dict:
    """Assemble the ordered per-criterion dict; EC3 is 'not_met' (content was retrieved)."""
    criteria = {}
    for name in LLM_CRITERIA:
        verdict = getattr(result, f"{name}_verdict")
        note = "" if verdict == "unclear" else getattr(result, f"{name}_note", "")
        criteria[name] = {"verdict": verdict, "note": note}
    criteria["EC3"] = {"verdict": "not_met", "note": "content retrieved"}
    return {name: criteria[name] for name in CRITERIA_ORDER}


def _decide(criteria: dict) -> str:
    for name, result in criteria.items():
        if name.startswith("IC") and result["verdict"] == "not_met":
            return "exclude"
        if name.startswith("EC") and result["verdict"] == "met":
            return "exclude"
    return "include"


def _reason(criteria: dict, decision: str) -> str:
    if decision == "include":
        return "all criteria met or unclear"
    failed = [name for name, r in criteria.items()
              if (name.startswith("IC") and r["verdict"] == "not_met")
              or (name.startswith("EC") and r["verdict"] == "met")]
    return "failed: " + ", ".join(failed)


def _new_record(survivor: dict) -> dict:
    return {
        "id": survivor["id"],
        "status": PENDING,
        "data": {
            "title": survivor.get("title", ""),
            "link": survivor.get("link") or survivor.get("doi_url", ""),
        },
        "screening": None,
    }


def _survivors(origin: str) -> list[dict]:
    data = json.loads(step_output_path(origin, 2).read_text(encoding="utf-8"))
    return [r for r in data["records"] if r.get("decision") == "include"]


def _load_manifest(origin: str, survivors: list[dict]) -> tuple[list[dict], str | None]:
    path = step_output_path(origin, 3)
    existing, model = {}, None
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        model = data.get("model")
        existing = {r["id"]: r for r in data.get("records", [])}
    records = [existing.get(s["id"]) or _new_record(s) for s in survivors]
    return records, model


def _save_manifest(origin: str, records: list[dict], model: str | None) -> None:
    screened = [r for r in records if r["status"] == SCREENED]
    included = sum(1 for r in screened if (r.get("screening") or {}).get("decision") == "include")
    output = {
        "origin": origin,
        "step": 3,
        "model": model,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(records),
        "by_status": {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)},
        "included": included,
        "excluded": len(screened) - included,
        "records": records,
    }
    path = step_output_path(origin, 3)
    ensure_parent(path)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")


def _mark_ec3(record: dict) -> None:
    criteria = {name: {"verdict": "unclear", "note": ""} for name in CRITERIA_ORDER}
    criteria["EC3"] = {"verdict": "met", "note": "content unavailable or inaccessible"}
    record["status"] = SCREENED
    record["screening"] = {"decision": "exclude", "confidence": "high",
                           "reason": "failed: EC3", "criteria": criteria}


def _phase_scrape(origin, survivors, by_id, save) -> None:
    if origin == "hf":
        _scrape_hf(survivors, by_id, save)
        return
    is_academic = _is_academic(origin)
    for survivor in survivors:
        record = by_id[survivor["id"]]
        if record["status"] != PENDING:
            continue
        if is_academic:
            details = scopus_gateway.fetch_details(survivor.get("eid", ""))
            if details:
                record["data"].update(
                    abstract=details.get("abstract", ""),
                    keywords=details.get("authorKeywords", []),
                    open_access=details.get("openAccess"),
                    language=details.get("language", ""),
                    publisher=details.get("publisher", ""),
                )
                record["status"] = SCRAPED
                print(f"[{origin}] scrape {survivor['id']}: "
                      f"{len(details.get('authorKeywords', []))} author keywords")
            else:
                _mark_ec3(record)
                print(f"[{origin}] scrape {survivor['id']}: FAILED -> EC3")
        else:
            path = content_path(origin, survivor["id"])
            cached = path.read_text(encoding="utf-8").strip() if path.exists() else ""
            if cached:  # reuse a page scraped in a prior run (e.g. after deleting step-3.json)
                record["status"] = SCRAPED
                print(f"[{origin}] scrape {survivor['id']}: reused cached {len(cached)} chars")
            else:
                content = scrape.scrape_markdown(survivor.get("link", ""))
                if content and content.strip():
                    ensure_parent(path)
                    path.write_text(content, encoding="utf-8")
                    record["status"] = SCRAPED
                    print(f"[{origin}] scrape {survivor['id']}: {len(content)} chars")
                else:
                    _mark_ec3(record)
                    print(f"[{origin}] scrape {survivor['id']}: FAILED -> EC3")
        save()  # persist after each item so an interruption resumes cleanly


def _scrape_hf(survivors, by_id, save) -> None:
    """HF Papers are arXiv papers: batch-fetch clean fields from the free arXiv API.

    A missing arXiv id is EC3; a batch miss is left pending (retried on the next run),
    so transient arXiv hiccups never turn into permanent exclusions.
    """
    pending = [s for s in survivors if by_id[s["id"]]["status"] == PENDING]
    id_by_item = {s["id"]: arxiv.arxiv_id_from_link(s.get("link", "")) for s in pending}
    details_by_arxiv = arxiv.fetch_many(list(id_by_item.values()))
    for survivor in pending:
        record = by_id[survivor["id"]]
        arxiv_id = id_by_item[survivor["id"]]
        details = details_by_arxiv.get(arxiv_id)
        if details:
            record["data"].update(
                abstract=details["abstract"],
                authors=details["authors"],
                publication_date=details["publication_date"],
                pdf_link=details["pdf_link"],
            )
            record["status"] = SCRAPED
            print(f"[hf] scrape {survivor['id']}: arXiv abstract ({len(details['abstract'])} chars)")
        elif not arxiv_id:
            _mark_ec3(record)
            print(f"[hf] scrape {survivor['id']}: no arXiv id -> EC3")
        else:
            print(f"[hf] scrape {survivor['id']}: arXiv miss, left pending for retry")
        save()


def _phase_summary(origin, survivors, by_id, save) -> None:
    if _is_academic(origin):
        print(f"[{origin}] summary: not applicable to academic sources; nothing to do")
        return
    # HF has a structured abstract (from arXiv) but no keywords: the LLM only extracts
    # keywords. Other grey sources have no structure: the LLM writes a full summary.
    is_hf = origin == "hf"
    prompt = HF_KEYWORDS_PROMPT if is_hf else SUMMARY_PROMPT
    model, _ = openrouter_model()
    agent = Agent(
        name="HF keyword extractor" if is_hf else "Summarizer",
        instructions=prompt.read_text(encoding="utf-8"),
        model=model,
        model_settings=ModelSettings(temperature=0.2),
        output_type=KeywordsResult if is_hf else SourceSummary,
    )
    for survivor in survivors:
        record = by_id[survivor["id"]]
        if record["status"] != SCRAPED:
            continue
        if is_hf:
            result: KeywordsResult = Runner.run_sync(agent, record["data"].get("abstract", "")).final_output
            record["data"]["keywords"] = result.keywords[:MAX_KEYWORDS]
            count = len(result.keywords[:MAX_KEYWORDS])
        else:
            content = content_path(origin, survivor["id"]).read_text(encoding="utf-8")
            summary: SourceSummary = Runner.run_sync(agent, f"CONTENT:\n{content}").final_output
            record["data"].update(
                summary=summary.summary,
                author=summary.author or "",
                publication_date=summary.publication_date or "",
                keywords=summary.keywords[:MAX_KEYWORDS],
            )
            count = len(summary.keywords[:MAX_KEYWORDS])
        record["status"] = SUMMARIZED
        print(f"[{origin}] summary {survivor['id']}: {count} keywords")
        save()


def _phase_screen(origin, survivors, by_id, state, save) -> None:
    ready = _ready_status(origin)
    model, model_name = openrouter_model()
    state["model"] = model_name
    agent = Agent(
        name="Abstract screener",
        instructions=SCREEN_PROMPT.read_text(encoding="utf-8"),
        model=model,
        model_settings=ModelSettings(temperature=0.2),
        output_type=ScreeningResult,
    )
    for survivor in survivors:
        record = by_id[survivor["id"]]
        if record["status"] != ready:
            continue
        data = record["data"]
        text = data.get("abstract") or data.get("summary") or ""
        user_msg = f"Summary: {text}\nKeywords: {', '.join(data.get('keywords', []))}"
        result: ScreeningResult = Runner.run_sync(agent, user_msg).final_output
        criteria = _criteria_from_result(result)
        decision = _decide(criteria)
        record["status"] = SCREENED
        record["screening"] = {"decision": decision, "confidence": result.confidence,
                               "reason": _reason(criteria, decision), "criteria": criteria}
        print(f"[{origin}] screen {survivor['id']}: {decision} ({result.confidence})")
        save()


def step3_screening(origin: str, substep: str | None = None) -> dict:
    survivors = _survivors(origin)
    records, model = _load_manifest(origin, survivors)
    by_id = {r["id"]: r for r in records}
    state = {"model": model}

    def save() -> None:
        _save_manifest(origin, records, state["model"])

    save()  # first action: the manifest is the source of truth
    counts = {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)}
    print(f"[{origin}] step 3: {len(records)} survivors; status={counts}")

    for phase in ([substep] if substep else SUBSTEPS):
        if phase == "scrape":
            _phase_scrape(origin, survivors, by_id, save)
        elif phase == "summary":
            _phase_summary(origin, survivors, by_id, save)
        elif phase == "screen":
            _phase_screen(origin, survivors, by_id, state, save)
        save()

    return {"origin": origin, "count": len(records),
            "by_status": {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)}}
