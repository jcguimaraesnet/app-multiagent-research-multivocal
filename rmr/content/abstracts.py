"""Academic abstract acquisition via free APIs (no Scopus entitlement needed).

Cascade by DOI (OpenAlex -> Semantic Scholar -> Crossref); if the record has no DOI, fall
back to an OpenAlex title search. Returns the abstract text, or None if not found.
"""

import os
import re

import requests

from rmr import config
from rmr.content import scrape


def _mailto() -> str:
    config.load_dotenv()
    return os.environ.get("CROSSREF_EMAIL", "").strip() or "research@example.com"


def _reconstruct(inverted_index) -> str | None:
    """Rebuild plain text from OpenAlex's abstract_inverted_index."""
    if not inverted_index:
        return None
    length = max(pos for positions in inverted_index.values() for pos in positions) + 1
    tokens = [""] * length
    for word, positions in inverted_index.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(tokens).strip() or None


def _openalex_by_doi(doi: str):
    try:
        r = requests.get(f"https://api.openalex.org/works/doi:{doi}",
                         params={"mailto": _mailto()}, timeout=20)
        if r.status_code != 200:
            return None
        return _reconstruct(r.json().get("abstract_inverted_index"))
    except requests.RequestException:
        return None


def _openalex_by_title(title: str):
    try:
        r = requests.get("https://api.openalex.org/works",
                         params={"filter": f"title.search:{title}", "per-page": 1,
                                 "mailto": _mailto()}, timeout=20)
        results = r.json().get("results", [])
        return _reconstruct(results[0].get("abstract_inverted_index")) if results else None
    except (requests.RequestException, IndexError, KeyError):
        return None


def _semantic_scholar_by_doi(doi: str):
    try:
        r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
                         params={"fields": "abstract"}, timeout=20)
        return r.json().get("abstract") if r.status_code == 200 else None
    except requests.RequestException:
        return None


def _crossref_by_doi(doi: str):
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}",
                         params={"mailto": _mailto()}, timeout=20)
        if r.status_code != 200:
            return None
        raw = r.json().get("message", {}).get("abstract")
        return re.sub(r"<[^>]+>", "", raw).strip() if raw else None
    except requests.RequestException:
        return None


def fetch_abstract(record: dict) -> str | None:
    """Return an abstract for an academic record, or None if unavailable anywhere.

    The cascade tries the free metadata aggregators by DOI, then an OpenAlex title search,
    and finally scrapes the publisher landing page (Firecrawl) as a last resort, since some
    abstracts are only on the page and not deposited with the aggregators. Each attempt is
    logged so the fallback path is visible.
    """
    item_id = record.get("id", "?")
    tried = []

    def attempt(name, value):
        tried.append(f"{name}={'ok' if value else 'x'}")
        return value

    doi = (record.get("doi") or "").strip()
    if doi:
        for name, source in (("openalex/doi", _openalex_by_doi),
                             ("s2/doi", _semantic_scholar_by_doi),
                             ("crossref/doi", _crossref_by_doi)):
            abstract = attempt(name, source(doi))
            if abstract:
                print(f"[abstract] {item_id}: via {name} ({'; '.join(tried)})")
                return abstract

    title = (record.get("title") or "").strip()
    if title:
        abstract = attempt("openalex/title", _openalex_by_title(title))
        if abstract:
            print(f"[abstract] {item_id}: via openalex/title ({'; '.join(tried)})")
            return abstract

    # Last resort: scrape the publisher landing page (paid Firecrawl call).
    url = record.get("doi_url") or record.get("preview_url") or ""
    if url:
        content = attempt("scrape/landing", scrape.scrape_markdown(url))
        if content:
            print(f"[abstract] {item_id}: via scrape/landing ({'; '.join(tried)})")
            return content

    print(f"[abstract] {item_id}: NOT FOUND ({'; '.join(tried)})")
    return None
