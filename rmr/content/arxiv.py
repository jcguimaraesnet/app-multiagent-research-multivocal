"""arXiv metadata retrieval (free API).

Hugging Face Papers are arXiv papers; the HF link carries the arXiv id
(huggingface.co/papers/<id>). We fetch the abstract, authors, publication date, and PDF
link straight from the arXiv API, which is clean and structured. arXiv has no author
keywords (only subject categories), so keywords are generated later by the LLM.
"""

import re
import time

import defusedxml.ElementTree as ET  # XXE/billion-laughs-safe parser
import requests

API_URL = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
BATCH_SIZE = 50


def arxiv_id_from_link(link: str) -> str:
    """Extract the arXiv id from a Hugging Face papers link (or any arXiv-ish URL)."""
    match = re.search(r"/papers/([^/?#]+)", link or "") or re.search(r"(\d{4}\.\d{4,5})", link or "")
    return match.group(1) if match else ""


def _parse_entry(entry) -> dict | None:
    abstract = " ".join((entry.findtext("a:summary", "", NS) or "").split())
    if not abstract:
        return None
    authors = [a.findtext("a:name", "", NS) for a in entry.findall("a:author", NS)]
    pdf = next((l.get("href") for l in entry.findall("a:link", NS) if l.get("title") == "pdf"), "")
    return {
        "title": " ".join((entry.findtext("a:title", "", NS) or "").split()),
        "abstract": abstract,
        "authors": [a for a in authors if a],
        "publication_date": entry.findtext("a:published", "", NS),
        "pdf_link": pdf,
    }


def fetch_many(arxiv_ids: list[str]) -> dict[str, dict]:
    """Fetch details for many ids in batched requests; return {arxiv_id: details}.

    Batching avoids the arXiv per-request rate limit that hits one-by-one fetching.
    """
    ids = [i for i in dict.fromkeys(arxiv_ids) if i]  # unique, keep order, drop empties
    results: dict[str, dict] = {}
    for start in range(0, len(ids), BATCH_SIZE):
        chunk = ids[start:start + BATCH_SIZE]
        root = None
        for attempt in range(4):
            try:
                resp = requests.get(API_URL, params={"id_list": ",".join(chunk),
                                                     "max_results": len(chunk)}, timeout=60)
            except requests.RequestException:
                break
            if resp.status_code == 429:  # rate limited: back off and retry
                time.sleep(5 * (attempt + 1))
                continue
            if resp.status_code != 200:
                break
            try:
                root = ET.fromstring(resp.text)
            except Exception:
                pass
            break
        if root is not None:
            for entry in root.findall("a:entry", NS):
                match = re.search(r"abs/(\d{4}\.\d{4,5})", entry.findtext("a:id", "", NS) or "")
                details = _parse_entry(entry)
                if match and details:
                    results[match.group(1)] = details
        if start + BATCH_SIZE < len(ids):
            time.sleep(3)  # polite between batches
    return results


def fetch_details(arxiv_id: str) -> dict | None:
    """Return {abstract, authors, publication_date, pdf_link} for an arXiv id, or None."""
    if not arxiv_id:
        return None
    try:
        resp = requests.get(API_URL, params={"id_list": arxiv_id}, timeout=30)
        if resp.status_code != 200:
            return None
        entry = ET.fromstring(resp.text).find("a:entry", NS)
    except Exception:
        return None
    if entry is None:
        return None
    abstract = " ".join((entry.findtext("a:summary", "", NS) or "").split())
    if not abstract:
        return None
    authors = [a.findtext("a:name", "", NS) for a in entry.findall("a:author", NS)]
    pdf = next((l.get("href") for l in entry.findall("a:link", NS) if l.get("title") == "pdf"), "")
    return {
        "title": " ".join((entry.findtext("a:title", "", NS) or "").split()),
        "abstract": abstract,
        "authors": [a for a in authors if a],
        "publication_date": entry.findtext("a:published", "", NS),
        "pdf_link": pdf,
    }
