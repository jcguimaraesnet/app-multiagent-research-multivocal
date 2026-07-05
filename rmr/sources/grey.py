"""Grey-literature source handlers (Google, GitHub, Hugging Face).

The three grey origins are Google web searches performed through Firecrawl's search
endpoint, differing only by the site: operator. Step 1 is a search-only pass that keeps
title + link; the page content is scraped later, at the screening steps. It does not use
the OpenAI Agents SDK.

Two execution rules follow the meta-protocol (Section 3.5) and our Firecrawl calibration:
- The search string is split into blocks (by population subgroups) so each query stays
  within the search engine's length budget (~32 words before Google starts truncating).
- The site: operator is placed at the FRONT of the query. Otherwise a long query is
  truncated at the tail and the site: filter is silently dropped, returning whole-web
  results instead of the intended domain.
"""

import json
import time
from datetime import datetime, timezone

import requests

from rmr import config
from rmr.paths import ensure_parent, step_output_path

SEARCH_URL = "https://api.firecrawl.dev/v2/search"

# --- Invariant execution rules for the grey channels ---
TBS = "cdr:1,cd_min:1/1/2022,cd_max:12/31/2025"  # after Dec 2021, up to 2025 (IC5)
COUNTRY = "US"
PER_CALL = 100        # Firecrawl's max results per search call
TARGET = 100          # unique links kept per origin
POP_CHUNK_SIZE = 3    # population terms per sub-query (keeps the query short enough)

# Hugging Face Papers is the successor of the discontinued Papers With Code, whose
# domain now redirects to huggingface.co/papers.
SITE_BY_ORIGIN = {
    "google": "",                          # whole web
    "github": "site:github.com",
    "hf": "site:huggingface.co/papers",
}

# Origin-prefixed identifier for each result (GO1, GH1, HF1, ...).
ID_PREFIX = {"google": "GO", "github": "GH", "hf": "HF"}


def _clause(terms):
    return " OR ".join(f'"{term}"' for term in terms)


def _chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _build_queries(origin, search_string):
    """One sub-query per population chunk, with the site: operator at the front."""
    site = SITE_BY_ORIGIN[origin]
    intervention = _clause(search_string["intervention"])
    outcome = _clause(search_string["outcome"])
    context = _clause(search_string["context"])
    queries = []
    for chunk in _chunks(search_string["population"], POP_CHUNK_SIZE):
        core = f"({_clause(chunk)}) AND ({intervention}) AND ({outcome}) AND ({context})"
        queries.append(f"{site} {core}".strip())
    return queries


def _search(origin, query, api_key):
    body = {"query": query, "limit": PER_CALL, "tbs": TBS,
            "sources": [{"type": "web"}], "country": COUNTRY}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(SEARCH_URL, json=body, headers=headers, timeout=180)
    if resp.status_code != 200:
        print(f"[{origin}] warning: HTTP {resp.status_code}: {resp.text[:160]}")
        return []
    return resp.json().get("data", {}).get("web", [])


def step1_initial_search(origin):
    """Run the identification search for a grey origin; write data/<origin>/step-1.json."""
    if origin not in SITE_BY_ORIGIN:
        raise ValueError(f"unknown grey origin: {origin}")
    api_key = config.require_env("FIRECRAWL_API_KEY")
    queries = _build_queries(origin, config.load_search_string())

    seen = set()
    records = []
    for query in queries:
        if len(records) >= TARGET:
            break
        for item in _search(origin, query, api_key):
            url = item.get("url", "")
            if url and url not in seen:
                seen.add(url)
                records.append({"title": item.get("title", ""), "link": url})
                if len(records) >= TARGET:
                    break
        print(f"[{origin}] unique so far: {len(records)}")
        time.sleep(1)

    # Assign a sequential, origin-prefixed identifier (GO1, GH1, HF1, ...) to each result.
    prefix = ID_PREFIX[origin]
    records = [{"id": f"{prefix}{i}", **record} for i, record in enumerate(records, start=1)]

    output = {
        "origin": origin,
        "step": 1,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "queries": queries,
        "count": len(records),
        "records": records,
    }
    path = step_output_path(origin, 1)
    ensure_parent(path)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{origin}] wrote {len(records)} records to {path}")
    return output
