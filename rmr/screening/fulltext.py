"""Step 4: full-text screening.

Implemented for all origins. For each step-3 survivor (decision = include), in a single pass
(no substeps), the full text is located, then the FINAL IC/EC screening is run over it. How
the full text is obtained differs by origin:

- **scopus**: full texts are paywalled, so the PDFs are downloaded manually into
  ``data/scopus/content/pdf/<id>.pdf``. The step converts each PDF to
  ``content/markdown/<id>.md`` with **pymupdf4llm** (reusing an existing conversion; an
  empty extraction, e.g. a scanned PDF, stays ``pending``). A missing PDF stays ``pending``.
  Status: ``pending -> converted -> screened``.
- **hf**: the PDF is downloaded automatically from the arXiv link captured in step 3, then
  converted like scopus. A transient download error stays ``pending`` (retried later); a
  paper that is permanently gone (withdrawn / HTTP 404) is excluded via EC3 (content
  availability). Status: ``pending -> converted -> screened``.
- **google/github**: the full page was already scraped in step 3 to
  ``data/<origin>/content/<id>.md``; step 4 reads it directly (no download/conversion). A
  missing/empty scrape stays ``pending``. Status: ``pending -> screened``.

The manifest ``data/<origin>/step-4.json`` is the source of truth; it is saved after every
item, so a re-run resumes cleanly and re-screening only touches records not yet ``screened``.

The screening reuses the step-3 machinery (the OpenAI Agents SDK ``ScreeningResult`` output
type and the criteria/decision helpers); only the prompt differs (final, over full text).
"""

import json
import time
from datetime import datetime, timezone

import pymupdf4llm
import requests
from agents import Agent, ModelSettings, Runner, set_tracing_disabled

from rmr.llm import openrouter_model
from rmr.paths import (PROJECT_ROOT, content_path, ensure_parent, markdown_path,
                       pdf_path, step_output_path)
from rmr.screening.abstract import (ScreeningResult, _criteria_from_result,
                                    _decide, _mark_ec3, _reason)

set_tracing_disabled(True)

SCREEN_PROMPT = PROJECT_ROOT / "prompts" / "step4-fulltext-screening.md"
FULLTEXT_MAX_CHARS = 150000  # cap the text sent to the model (a full paper fits comfortably)
SCREEN_MAX_TOKENS = 1500    # output budget: the 15-field JSON with short notes fits easily
SCREEN_ATTEMPTS = 2         # retry a malformed/failed response before leaving it pending
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

SUPPORTED = ("scopus", "google", "github", "hf")
GREY = ("google", "github")
PDF_ORIGINS = ("scopus", "hf")  # full text comes from a PDF (converted with pymupdf4llm)

PENDING, CONVERTED, SCREENED = "pending", "converted", "screened"


def _statuses(origin: str) -> list[str]:
    # PDF origins add a conversion status; grey pages are already scraped in step 3.
    return [PENDING, CONVERTED, SCREENED] if origin in PDF_ORIGINS else [PENDING, SCREENED]


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


def _ensure_pdf(origin: str, record: dict, survivor: dict) -> bool:
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
        # Read the link from the fresh step-3 survivor (the step-4 record does not carry it).
        url = survivor.get("data", {}).get("pdf_link", "")
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
            _mark_ec3(record)  # withdrawn/unavailable -> excluded (EC3), status becomes screened
            print(f"[hf] convert {rid}: PDF not found (withdrawn) -> excluded (EC3)")
            return False
        record["status"] = PENDING
        print(f"[hf] convert {rid}: PDF download error -> pending (retry later)")
        return False
    record["status"] = PENDING  # scopus: supplied manually
    print(f"[{origin}] convert {rid}: no PDF at {pdf} -> pending")
    return False


def _ensure_markdown(origin: str, record: dict, survivor: dict, save) -> str:
    """Return the full-text Markdown for a record, acquiring/converting the PDF if needed.

    Returns "" when the record is not ready to be screened (no PDF, or empty extraction),
    leaving its status as ``pending`` so the file can be supplied/retried on a re-run.
    """
    rid = record["id"]
    if not _ensure_pdf(origin, record, survivor):
        return ""  # _ensure_pdf already set the status (pending, or screened via EC3)
    pdf = pdf_path(origin, rid)

    md = markdown_path(origin, rid)
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
    path = content_path(origin, rid)
    text = path.read_text(encoding="utf-8").strip() if path.exists() else ""
    if not text:
        record["status"] = PENDING
        print(f"[{origin}] screen {rid}: no scraped content at {path} -> pending")
    return text


def _screen_once(agent, text: str, origin: str, rid: str):
    """Run the screener, retrying a failed/malformed response. Returns the result or None.

    A truncated or invalid JSON from the model raises inside the SDK; catching it here keeps
    one bad item from aborting the whole batch (the item stays pending and is retried later).
    """
    for attempt in range(1, SCREEN_ATTEMPTS + 1):
        try:
            return Runner.run_sync(agent, f"FULL TEXT:\n{text}").final_output
        except Exception as error:  # noqa: BLE001 - includes ModelBehaviorError (bad JSON)
            print(f"[{origin}] screen {rid}: attempt {attempt}/{SCREEN_ATTEMPTS} failed "
                  f"({type(error).__name__}); {'retrying' if attempt < SCREEN_ATTEMPTS else 'left pending'}")
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
    agent = Agent(
        name="Full-text screener",
        instructions=SCREEN_PROMPT.read_text(encoding="utf-8"),
        model=llm,
        # Give the structured JSON room to finish; a cut-off response is invalid JSON.
        model_settings=ModelSettings(temperature=0.2, max_tokens=SCREEN_MAX_TOKENS),
        output_type=ScreeningResult,
    )

    for survivor in survivors:
        record = by_id[survivor["id"]]
        if record["status"] == SCREENED:
            continue
        full_text = (_grey_fulltext(origin, record) if origin in GREY
                     else _ensure_markdown(origin, record, survivor, save))
        if not full_text:
            save()  # persist the pending status
            continue
        text = full_text[:FULLTEXT_MAX_CHARS]
        if len(full_text) > FULLTEXT_MAX_CHARS:
            print(f"[{origin}] screen {survivor['id']}: text truncated "
                  f"{len(full_text)} -> {FULLTEXT_MAX_CHARS} chars")
        result = _screen_once(agent, text, origin, survivor["id"])
        if result is None:  # keep this item pending; a bad response must not abort the batch
            save()
            continue
        criteria = _criteria_from_result(result)
        decision = _decide(criteria)
        record["status"] = SCREENED
        record["screening"] = {"decision": decision, "confidence": result.confidence,
                               "reason": _reason(criteria, decision), "criteria": criteria}
        print(f"[{origin}] screen {survivor['id']}: {decision} ({result.confidence})")
        save()

    return {"origin": origin, "count": len(records),
            "by_status": {st: sum(1 for r in records if r["status"] == st) for st in _statuses(origin)}}
