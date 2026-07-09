"""Step 4: full-text screening.

Implemented for all origins. For each step-3 survivor (decision = include), in a single pass
(no substeps), the full text is located, then TWO LLM calls run over it:
1. **answer**: extract the research-question answers (RQa-RQh), each a `note` plus a `value`
   from a fixed set, stored under the record's ``answers`` object (status -> answered).
2. **screen**: the FINAL IC/EC screening, given BOTH the full text and the research answers
   as context (status -> screened).

How the full text is obtained differs by origin:

- **scopus**: full texts are paywalled, so the PDFs are downloaded manually into
  ``data/scopus/content/pdf/<id>.pdf``. The step converts each PDF to ``content/full/<id>.md``
  with **pymupdf4llm** (reusing an existing conversion; an empty extraction, e.g. a scanned
  PDF, stays ``pending``). A missing PDF stays ``pending``.
  Status: ``pending -> converted -> answered -> screened``.
- **hf**: the PDF is downloaded automatically from the arXiv link captured in step 3, then
  converted like scopus. A transient download error stays ``pending`` (retried later); a
  paper that is permanently gone (withdrawn / HTTP 404) is excluded via EC3 (content
  availability). Status: ``pending -> converted -> answered -> screened``.
- **google/github**: the full page was already scraped in step 3 to
  ``data/<origin>/content/full/<id>.md``; step 4 reads it directly (no download/conversion).
  A missing/empty scrape stays ``pending``. Status: ``pending -> answered -> screened``.

The manifest ``data/<origin>/step-4-screen-full.json`` is the source of truth; it is saved
after every phase, so a re-run resumes cleanly (an answered-but-not-screened record only runs
screen; a screened record is skipped).

The screening reuses the step-3 machinery (the OpenAI Agents SDK ``ScreeningResult`` output
type and the criteria/decision helpers); only the prompt differs (final, over full text).
"""

import json
import time
from datetime import datetime, timezone
from typing import Literal

import pymupdf4llm
import requests
from agents import Agent, ModelSettings, Runner, set_tracing_disabled
from pydantic import BaseModel

from rmr.llm import openrouter_model
from rmr.paths import (PROJECT_ROOT, ensure_parent, full_path, pdf_path,
                       step_output_path)
from rmr.screening.abstract import read_abstract

set_tracing_disabled(True)

ANSWER_PROMPT = PROJECT_ROOT / "prompts" / "step4-research-answers.md"
SCREEN_PROMPT = PROJECT_ROOT / "prompts" / "step4-fulltext-screening.md"
FULLTEXT_MAX_CHARS = 150000  # cap the text sent to the model (a full paper fits comfortably)
ANSWER_MAX_TOKENS = 2000    # output budget: the 8 research answers (note + value) fit easily
SCREEN_MAX_TOKENS = 2000    # output budget: the binary-verdict JSON with the extra IC2/IC3 fields
SCREEN_ATTEMPTS = 2         # retry a malformed/failed response before leaving it pending
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

SUPPORTED = ("scopus", "google", "github", "hf")
GREY = ("google", "github")
PDF_ORIGINS = ("scopus", "hf")  # full text comes from a PDF (converted with pymupdf4llm)

PENDING, CONVERTED, ANSWERED, SCREENED = "pending", "converted", "answered", "screened"


def _statuses(origin: str) -> list[str]:
    # PDF origins add a conversion status; grey pages are already scraped in step 3.
    base = [PENDING, CONVERTED] if origin in PDF_ORIGINS else [PENDING]
    return base + [ANSWERED, SCREENED]


# --- Research-question answers (the `answered` phase) ---
# Each answer carries a free-text `note` and a `value` classification drawn from a fixed set.
# The OpenAI Agents SDK enforces these Literal enums via the structured output_type, so the
# model can only return an allowed value. RQf accepts several values (a list); the rest one.

class RQaAnswer(BaseModel):
    note: str
    value: Literal["Product / vendor website", "Code repository", "Blog / article",
                   "Cloud platform", "Preprint", "Academic Paper", "Course / educational",
                   "Other"]
    evidence: str  # a short verbatim excerpt from the source that grounds `value`


class RQbAnswer(BaseModel):
    note: str
    value: Literal["General-purpose (GP)", "Application generation (AG)", "Frontend-only (FE)",
                   "Automation (AU)", "Domain or language-specific"]
    evidence: str


class RQcAnswer(BaseModel):
    note: str
    value: Literal["Open-source / free", "Commercial (paid, freemium, enterprise)", "Unspecified"]
    evidence: str


class RQdAnswer(BaseModel):
    note: str
    value: Literal["Technical limitations", "Operational constraints", "Legal and ethical concerns"]
    evidence: str


class RQeAnswer(BaseModel):
    note: str
    value: Literal["Production-ready", "Experimental or beta phase"]
    evidence: str


class RQfAnswer(BaseModel):
    note: str
    value: list[Literal["Docs/Tutorial/User Manual", "Forum", "GitHub issue trackers",
                        "Release notes", "Slack/Discord Community"]]
    evidence: str


class RQgAnswer(BaseModel):
    note: str
    value: Literal["Developers", "DevOps professionals", "QA/Testers", "Others"]
    evidence: str


class RQhAnswer(BaseModel):
    note: str
    value: Literal["Industrial case studies", "Large-scale user studies", "Unspecified"]
    evidence: str


class ResearchAnswers(BaseModel):
    # Root attribute: the name of the tool/technology/agent/framework/technique the source is
    # about. A short name (at most a composite name, e.g. "GitHub Copilot"), not a description.
    solution_name: str
    RQa: RQaAnswer
    RQb: RQbAnswer
    RQc: RQcAnswer
    RQd: RQdAnswer
    RQe: RQeAnswer
    RQf: RQfAnswer
    RQg: RQgAnswer
    RQh: RQhAnswer


def _answers_text(answers: dict) -> str:
    """Render the stored answers as compact lines to inject into the screening prompt."""
    lines = []
    if answers.get("solution_name"):
        lines.append(f"Solution name: {answers['solution_name']}")
    for rq, answer in answers.items():
        if not isinstance(answer, dict):  # skip the root solution_name (already rendered)
            continue
        value = answer.get("value")
        value = ", ".join(value) if isinstance(value, list) else value
        lines.append(f"{rq} [{value}]: {answer.get('note', '')}")
    return "\n".join(lines)


# --- Final full-text screening (the `screened` phase) ---
# Unlike step 3, step 4 is BINARY (no "unclear"): every criterion is either met or not_met.
# IC2 and IC3 carry extra classification fields (see the prompt). EC3 (content availability)
# is set by code; the rest come from the screener agent.

CRITERIA_ORDER = ["IC1", "IC2", "IC3", "IC4", "IC5", "EC3", "EC4", "EC5"]
LLM_CRITERIA = ["IC1", "IC2", "IC3", "IC4", "IC5", "EC4", "EC5"]

Verdict = Literal["met", "not_met"]


class FullTextScreeningResult(BaseModel):
    IC1_verdict: Verdict
    IC1_note: str = ""
    IC2_verdict: Verdict
    IC2_note: str = ""
    # Extra IC2 classification; "" when it fits none (then IC2 is not_met).
    IC2_type: Literal["agent", "tool", "language model", "extension", "IDE",
                      "technique/solution", ""] = ""
    IC2_software_engineering_activity: str = ""  # a coding-phase activity, or "" if none
    IC3_verdict: Verdict
    IC3_note: str = ""
    IC3_type: Literal["primary study", "empirical case", ""] = ""  # "" when neither fits
    IC4_verdict: Verdict
    IC4_note: str = ""
    IC5_verdict: Verdict
    IC5_note: str = ""
    EC4_verdict: Verdict
    EC4_note: str = ""
    EC5_verdict: Verdict
    EC5_note: str = ""
    confidence: Literal["low", "medium", "high"]


def _criteria_from_fulltext(result: FullTextScreeningResult) -> dict:
    """Assemble the ordered per-criterion dict; EC3 is 'not_met' (content was retrieved)."""
    criteria = {}
    for name in LLM_CRITERIA:
        entry = {"verdict": getattr(result, f"{name}_verdict"),
                 "note": getattr(result, f"{name}_note", "")}
        if name == "IC2":
            entry["type"] = result.IC2_type
            entry["software_engineering_activity"] = result.IC2_software_engineering_activity
        elif name == "IC3":
            entry["type"] = result.IC3_type
        criteria[name] = entry
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
        return "all criteria met"
    failed = [name for name, r in criteria.items()
              if (name.startswith("IC") and r["verdict"] == "not_met")
              or (name.startswith("EC") and r["verdict"] == "met")]
    return "failed: " + ", ".join(failed)


def _mark_unavailable(record: dict) -> None:
    """Content could not be retrieved: exclude via EC3 (binary), without an LLM screening."""
    record["status"] = SCREENED
    record["screening"] = {
        "decision": "exclude", "confidence": "high", "reason": "failed: EC3",
        "criteria": {"EC3": {"verdict": "met", "note": "content unavailable or inaccessible"}},
    }


def _survivors(origin: str) -> list[dict]:
    """Step-3 records that were included (the ones to read in full)."""
    data = json.loads(step_output_path(origin, 3).read_text(encoding="utf-8"))
    return [r for r in data.get("records", [])
            if (r.get("screening") or {}).get("decision") == "include"]


def _new_record(survivor: dict) -> dict:
    data = survivor.get("data", {})
    return {
        "id": survivor["id"],
        "status": PENDING,
        "data": {"title": data.get("title", ""), "link": data.get("link", "")},
        "answers": None,
        "screening": None,
    }


def _load_manifest(origin: str, survivors: list[dict]) -> tuple[list[dict], str | None]:
    path = step_output_path(origin, 4)
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
        "step": 4,
        "model": model,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(records),
        "by_status": {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)},
        "included": included,
        "excluded": len(screened) - included,
        "records": records,
    }
    path = step_output_path(origin, 4)
    ensure_parent(path)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")


def _download_pdf(url: str, dest) -> str:
    """Download a PDF to ``dest``. Returns "ok", "not_found" (withdrawn / 404 / 410), or
    "error" (transient: network failure, timeout, 5xx)."""
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=90)
    except requests.RequestException:
        return "error"
    if resp.status_code in (404, 410):
        return "not_found"
    if resp.status_code != 200 or not resp.content:
        return "error"
    ensure_parent(dest)
    dest.write_bytes(resp.content)
    return "ok"


def _ensure_pdf(origin: str, record: dict) -> bool:
    """Ensure ``content/pdf/<id>.pdf`` exists and set the record status on failure.

    scopus PDFs are placed manually (a missing one stays ``pending``); hf PDFs are downloaded
    from the arXiv link. A permanently unavailable hf paper (withdrawn / 404) is excluded via
    EC3 (content availability); a transient download error stays ``pending`` for retry.
    Returns True only when a PDF is available.
    """
    rid = record["id"]
    pdf = pdf_path(origin, rid)
    if pdf.exists():
        return True
    if origin == "hf":
        # The arXiv link lives in the captured-content file (content/abstract/<id>.json).
        url = read_abstract("hf", rid).get("pdf_link", "")
        record["data"]["pdf_link"] = url  # record what we used, for traceability
        if not url:
            record["status"] = PENDING
            print(f"[hf] convert {rid}: no arXiv PDF link -> pending")
            return False
        outcome = _download_pdf(url, pdf)
        if outcome == "ok":
            print(f"[hf] convert {rid}: downloaded PDF from {url}")
            time.sleep(1)  # be polite to arXiv between downloads
            return True
        if outcome == "not_found":
            _mark_unavailable(record)  # withdrawn -> excluded (EC3), status becomes screened
            print(f"[hf] convert {rid}: PDF not found (withdrawn) -> excluded (EC3)")
            return False
        record["status"] = PENDING
        print(f"[hf] convert {rid}: PDF download error -> pending (retry later)")
        return False
    record["status"] = PENDING  # scopus: supplied manually
    print(f"[{origin}] convert {rid}: no PDF at {pdf} -> pending")
    return False


def _ensure_markdown(origin: str, record: dict, save) -> str:
    """Return the full-text Markdown for a record, acquiring/converting the PDF if needed.

    Returns "" when the record is not ready to be screened (no PDF, or empty extraction),
    leaving its status as ``pending`` so the file can be supplied/retried on a re-run.
    """
    rid = record["id"]
    if not _ensure_pdf(origin, record):
        return ""  # _ensure_pdf already set the status (pending, or screened via EC3)
    pdf = pdf_path(origin, rid)

    md = full_path(origin, rid)
    if md.exists():
        cached = md.read_text(encoding="utf-8").strip()
        if cached:  # reuse a previous conversion, never reconvert
            record["data"]["markdown_chars"] = len(cached)
            if record["status"] == PENDING:
                record["status"] = CONVERTED
            print(f"[{origin}] convert {rid}: reused cached markdown ({len(cached)} chars)")
            return cached

    try:
        markdown = (pymupdf4llm.to_markdown(str(pdf)) or "").strip()
    except Exception as error:  # a corrupt/unreadable PDF must not abort the whole run
        record["status"] = PENDING
        print(f"[{origin}] convert {rid}: conversion error ({error}) -> pending")
        return ""
    if not markdown:
        record["status"] = PENDING
        print(f"[{origin}] convert {rid}: empty extraction (scanned PDF?) -> pending")
        return ""

    ensure_parent(md)
    md.write_text(markdown, encoding="utf-8")
    record["data"]["markdown_chars"] = len(markdown)
    record["status"] = CONVERTED
    print(f"[{origin}] convert {rid}: {len(markdown)} chars")
    save()
    return markdown


def _grey_fulltext(origin: str, record: dict) -> str:
    """Full text of a grey source: the page already scraped in step 3.

    Returns "" (leaving the record ``pending``) when the step-3 scrape is missing/empty.
    """
    rid = record["id"]
    path = full_path(origin, rid)
    text = path.read_text(encoding="utf-8").strip() if path.exists() else ""
    if not text:
        record["status"] = PENDING
        print(f"[{origin}] screen {rid}: no scraped content at {path} -> pending")
    return text


def _run_agent(agent, user_msg: str, origin: str, rid: str, label: str):
    """Run an agent, retrying a failed/malformed response. Returns the output or None.

    A truncated or invalid JSON from the model raises inside the SDK; catching it here keeps
    one bad item from aborting the whole batch (the item is left as-is and retried later).
    """
    for attempt in range(1, SCREEN_ATTEMPTS + 1):
        try:
            return Runner.run_sync(agent, user_msg).final_output
        except Exception as error:  # noqa: BLE001 - includes ModelBehaviorError (bad JSON)
            print(f"[{origin}] {label} {rid}: attempt {attempt}/{SCREEN_ATTEMPTS} failed "
                  f"({type(error).__name__}); {'retrying' if attempt < SCREEN_ATTEMPTS else 'left for retry'}")
    return None


def step4_fulltext_screening(origin: str) -> dict:
    if origin not in SUPPORTED:
        raise NotImplementedError(
            f"step 4 ('full-text screening') is not implemented for '{origin}' "
            f"(supported: {', '.join(SUPPORTED)})"
        )

    survivors = _survivors(origin)
    records, model = _load_manifest(origin, survivors)
    by_id = {r["id"]: r for r in records}
    state = {"model": model}

    def save() -> None:
        _save_manifest(origin, records, state["model"])

    save()  # first action: the manifest is the source of truth
    counts = {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)}
    print(f"[{origin}] step 4: {len(records)} survivors; status={counts}")

    llm, model_name = openrouter_model()
    state["model"] = model_name
    # Give the structured JSON room to finish; a cut-off response is invalid JSON.
    answer_agent = Agent(
        name="Research-question answerer",
        instructions=ANSWER_PROMPT.read_text(encoding="utf-8"),
        model=llm,
        model_settings=ModelSettings(temperature=0.2, max_tokens=ANSWER_MAX_TOKENS),
        output_type=ResearchAnswers,
    )
    screen_agent = Agent(
        name="Full-text screener",
        instructions=SCREEN_PROMPT.read_text(encoding="utf-8"),
        model=llm,
        model_settings=ModelSettings(temperature=0.2, max_tokens=SCREEN_MAX_TOKENS),
        output_type=FullTextScreeningResult,
    )

    for survivor in survivors:
        rid = survivor["id"]
        record = by_id[rid]
        if record["status"] == SCREENED:
            continue
        full_text = (_grey_fulltext(origin, record) if origin in GREY
                     else _ensure_markdown(origin, record, save))
        if not full_text:
            save()  # persist the pending status (or EC3 exclusion set while acquiring)
            continue
        text = full_text[:FULLTEXT_MAX_CHARS]
        if len(full_text) > FULLTEXT_MAX_CHARS:
            print(f"[{origin}] {rid}: text truncated {len(full_text)} -> {FULLTEXT_MAX_CHARS} chars")

        # Answer phase: extract the research-question answers first (status -> answered).
        if record["status"] != ANSWERED:
            answers = _run_agent(answer_agent, f"FULL TEXT:\n{text}", origin, rid, "answer")
            if answers is None:  # a bad response must not abort the batch; retry next run
                save()
                continue
            record["answers"] = answers.model_dump()
            record["status"] = ANSWERED
            print(f"[{origin}] answer {rid}: {record['answers']['solution_name']!r} | "
                  f"RQb={record['answers']['RQb']['value']}, RQe={record['answers']['RQe']['value']}")
            save()

        # Screen phase: inject BOTH the full text and the research answers.
        screen_msg = (f"FULL TEXT:\n{text}\n\nRESEARCH ANSWERS (extracted from this source):\n"
                      f"{_answers_text(record['answers'])}")
        result = _run_agent(screen_agent, screen_msg, origin, rid, "screen")
        if result is None:
            save()
            continue
        criteria = _criteria_from_fulltext(result)
        decision = _decide(criteria)
        record["status"] = SCREENED
        record["screening"] = {"decision": decision, "confidence": result.confidence,
                               "reason": _reason(criteria, decision), "criteria": criteria}
        print(f"[{origin}] screen {rid}: {decision} ({result.confidence})")
        save()

    return {"origin": origin, "count": len(records),
            "by_status": {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)}}
