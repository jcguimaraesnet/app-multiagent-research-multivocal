"""Grey-literature source handlers (Google, GitHub, Hugging Face).

The three grey origins are Google web searches performed through Firecrawl's search
endpoint, differing only by the site: operator. Step 1 is a search-only pass that keeps
title + link; the page content is scraped later, at the screening steps. It does not use
the OpenAI Agents SDK.

Three execution rules follow the meta-protocol (Section 3.5) and our Firecrawl calibration:
- The search string is split into blocks (by population subgroups) so each query stays
  within the search engine's length budget (~32 words before Google starts truncating).
- The site: operator is placed at the FRONT of the query. Otherwise a long query is
  truncated at the tail and the site: filter is silently dropped, returning whole-web
  results instead of the intended domain.
- The channel target of 100 UNIQUE results is reached from a SINGLE fetch per query (no
  repeated network rounds). Each query fetches double its share up front
  (FETCH_MULTIPLIER * TARGET_TOTAL / N, i.e. 50 for 4 queries) into an in-memory buffer.
  Synthesis then unions the first TARGET_TOTAL / N of each buffer (25 each) and deduplicates;
  if fewer than 100 unique remain, it draws more from the SAME buffers proportionally and
  deduplicates again, until 100 unique are collected or the buffers are exhausted. Duplicates
  dropped here are the EC2 exclusion; the set is trimmed to exactly TARGET_TOTAL. Fetching
  double is the optimistic assumption that the buffers hold enough to reach 100 after dedup.
"""

import json
import math
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from rmr import config
from rmr.content import titles
from rmr.paths import ensure_parent, step_output_path

SEARCH_URL = "https://api.firecrawl.dev/v2/search"

# --- Invariant execution rules for the grey channels ---
TBS = "cdr:1,cd_min:1/1/2022,cd_max:12/31/2025"  # after Dec 2021, up to 2025 (IC5)
COUNTRY = "US"
TARGET_TOTAL = 100    # channel target of UNIQUE results across ALL sub-queries (meta-protocol §3.5)
POP_CHUNK_SIZE = 3    # population terms per sub-query (keeps the query short enough)
FETCH_MULTIPLIER = 2  # fetch this multiple of each query's share up front, to top up in memory
MAX_PER_QUERY = 100   # practical per-query ceiling (Google returns at most ~100 per query)

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


def _search(origin, query, api_key, limit):
    body = {"query": query, "limit": limit, "tbs": TBS,
            "sources": [{"type": "web"}], "country": COUNTRY}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(SEARCH_URL, json=body, headers=headers, timeout=180)
    if resp.status_code != 200:
        print(f"[{origin}] warning: HTTP {resp.status_code}: {resp.text[:160]}")
        return []
    return resp.json().get("data", {}).get("web", [])


def _sanitize_link(url):
    """Normalize a result URL before deduplication. GitHub links to a file, issue,
    discussion, pull request, etc. are reduced to the repository root
    (``https://github.com/<owner>/<repo>``), so different pages of the same repository
    collapse into one record. Non-GitHub URLs are returned unchanged.
    """
    parsed = urlparse(url)
    if parsed.netloc.lower().removeprefix("www.") == "github.com":
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2:
            return f"https://github.com/{parts[0]}/{parts[1]}"
    return url


def _collect(buffers, takes):
    """Union the first ``takes[i]`` results of each buffer, deduplicated by URL (EC2).

    Links are sanitized before the dedup check (see ``_sanitize_link``).
    """
    seen, records = set(), []
    for buffer, take in zip(buffers, takes):
        for item in buffer[:take]:
            original = item.get("url", "")
            url = _sanitize_link(original)
            if url and url not in seen:
                seen.add(url)
                # When the link was sanitized, the snippet title describes the old page
                # (an issue/file/discussion); blank it so step-1 title recovery fetches the
                # title of the sanitized URL (the repository root).
                title = "" if url != original else item.get("title", "")
                records.append({"title": title, "link": url})
    return records


def step1_initial_search(origin):
    """Run the identification search for a grey origin; write data/<origin>/step-1-initial-search.json."""
    if origin not in SITE_BY_ORIGIN:
        raise ValueError(f"unknown grey origin: {origin}")
    api_key = config.require_env("FIRECRAWL_API_KEY")
    queries = _build_queries(origin, config.load_search_string())
    n = len(queries)
    base = max(1, math.ceil(TARGET_TOTAL / n))                     # per-query share (25 for 4)
    fetch_limit = min(MAX_PER_QUERY, base * FETCH_MULTIPLIER)      # fetch double up front (50)

    # ONE network fetch per query, buffered in memory.
    buffers = []
    for query in queries:
        buffers.append(_search(origin, query, api_key, fetch_limit))
        time.sleep(1)
    print(f"[{origin}] fetched {sum(len(b) for b in buffers)} results across {n} queries "
          f"(<= {fetch_limit} each)")

    # Synthesis: start at the per-query share, then top up proportionally FROM THE BUFFERS
    # (no more network) until 100 unique or the buffers are exhausted at the fetched depth.
    takes = [min(len(buffers[i]), base) for i in range(n)]
    while True:
        records = _collect(buffers, takes)
        if len(records) >= TARGET_TOTAL:
            break
        bump = max(1, math.ceil((TARGET_TOTAL - len(records)) / n))
        new_takes = [min(len(buffers[i]), takes[i] + bump) for i in range(n)]
        if new_takes == takes:  # every buffer exhausted at its fetched depth
            break
        takes = new_takes

    records = records[:TARGET_TOTAL]  # exactly TARGET_TOTAL unique (or fewer if unreachable)
    print(f"[{origin}] {len(records)} unique after dedup (takes={takes})")
    if len(records) < TARGET_TOTAL:
        print(f"[{origin}] warning: only {len(records)} unique from the fetched buffers "
              f"(< {TARGET_TOTAL}); consider a larger FETCH_MULTIPLIER")

    # Assign a sequential, origin-prefixed identifier (GO1, GH1, HF1, ...) to each result.
    prefix = ID_PREFIX[origin]
    records = [{"id": f"{prefix}{i}", **record} for i, record in enumerate(records, start=1)]

    # Recover the full title now (search snippets are truncated), so step 2 screens the
    # complete title and needs no network access of its own.
    titles.enrich_titles(origin, records)

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
