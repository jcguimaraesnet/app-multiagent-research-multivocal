"""Scopus source handlers.

Step 1 (initial complete search) is a direct call to the Scopus Search API; it does
not use the OpenAI Agents SDK (that enters at the LLM screening steps 2-4). The search
terms are read from ``protocol-settings/2-search-string.json``; the execution rules
below (field scope, year window, subject area, document type, language) are the
invariant Scopus-channel parameters and therefore live in code, not in the settings.
"""

import json
import time
from datetime import datetime, timezone

import requests

from rmr import config
from rmr.paths import ensure_parent, step_output_path

SEARCH_URL = "https://api.elsevier.com/content/search/scopus"

# --- Invariant execution rules for the Scopus channel ---
FIELD_SCOPE = "TITLE-ABS-KEY"  # match terms in title, abstract, and author keywords
START_YEAR = 2021              # PUBYEAR > 2021
END_YEAR = 2026                # PUBYEAR < 2026
SUBJAREA = "COMP"              # Computer Science subject area
DOCTYPE = "ar"                 # articles only (rapid-review scope)
LANGUAGE = "English"
PAGE_SIZE = 25                 # the free Scopus API caps at 25 records per request


def build_query(search_string: dict) -> str:
    """Assemble the Scopus query string from the PICOC term lists."""
    def clause(terms):
        return " OR ".join(f'"{term}"' for term in terms)

    population = clause(search_string["population"])
    intervention = clause(search_string["intervention"])
    outcome = clause(search_string["outcome"])
    context = clause(search_string["context"])

    core = f"{FIELD_SCOPE}(({population}) AND ({intervention}) AND ({outcome}) AND ({context}))"
    return (
        f"{core} AND PUBYEAR > {START_YEAR} AND PUBYEAR < {END_YEAR} "
        f"AND SUBJAREA({SUBJAREA}) AND DOCTYPE({DOCTYPE}) AND LANGUAGE({LANGUAGE})"
    )


def _parse_entry(item: dict) -> dict:
    """Extract the fields we keep from one Scopus search-result entry."""
    doi = item.get("prism:doi", "")
    links = {li.get("@ref"): li.get("@href") for li in item.get("link", []) if li.get("@ref")}
    sid = item.get("dc:identifier", "").replace("SCOPUS_ID:", "").replace("SCOPUS:", "")
    return {
        "sid": sid,
        "eid": item.get("eid", ""),
        "doi": doi,
        "doi_url": f"https://doi.org/{doi}" if doi else "",
        "preview_url": links.get("scopus", ""),
        "api_url": item.get("prism:url", ""),
        "title": item.get("dc:title", ""),
        "authors": item.get("dc:creator", ""),
        "publicationDate": item.get("prism:coverDate", ""),
        "publicationVenue": item.get("prism:publicationName", ""),
    }


def step1_initial_search() -> dict:
    """Run the identification search on Scopus and write ``data/scopus/step-1.json``."""
    api_key = config.require_env("SCOPUS_API_KEY")
    query = build_query(config.load_search_string())
    headers = {"Accept": "application/json", "X-ELS-APIKey": api_key}

    # First request also tells us the total number of results.
    first = requests.get(
        SEARCH_URL, headers=headers,
        params={"query": query, "count": PAGE_SIZE, "start": 0}, timeout=30,
    )
    first.raise_for_status()
    results = first.json().get("search-results", {})
    total = int(results.get("opensearch:totalResults", 0))
    print(f"[scopus] total results: {total}")

    records = []
    for start in range(0, total, PAGE_SIZE):
        if start == 0:
            entries = results.get("entry", [])
        else:
            time.sleep(0.2)  # be gentle with the API between pages
            resp = requests.get(
                SEARCH_URL, headers=headers,
                params={"query": query, "count": PAGE_SIZE, "start": start}, timeout=30,
            )
            resp.raise_for_status()
            entries = resp.json().get("search-results", {}).get("entry", [])
        # A zero-result response returns a single entry carrying an "error" field.
        if not entries or (len(entries) == 1 and "error" in entries[0]):
            break
        records.extend(_parse_entry(entry) for entry in entries)
        print(f"[scopus] fetched {min(start + PAGE_SIZE, total)}/{total}")

    # Assign a sequential, origin-prefixed identifier (SC1, SC2, ...) to each result.
    records = [{"id": f"SC{i}", **record} for i, record in enumerate(records, start=1)]

    output = {
        "origin": "scopus",
        "step": 1,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "total_results": total,
        "count": len(records),
        "records": records,
    }
    path = step_output_path("scopus", 1)
    ensure_parent(path)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[scopus] wrote {len(records)} records to {path}")
    return output
