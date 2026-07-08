"""Authenticated Scopus gateway retrieval.

The Scopus web app loads each record's data (abstract, author keywords, etc.) from an
internal JSON endpoint keyed by the EID:

    https://www.scopus.com/gateway/doc-details/documents/<eid>

A plain request is blocked by anti-bot protection (403), but Firecrawl's headless browser
with the user's session cookie and an enhanced proxy gets through. The cookie is read from
data/.scopus_cookie.txt (git-ignored) and expires, so it must be valid at run time.
"""

import json
import re

import requests

from rmr import config
from rmr.paths import DATA_DIR

GATEWAY_URL = "https://www.scopus.com/gateway/doc-details/documents/{eid}"
FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v2/scrape"
COOKIE_FILE = DATA_DIR / ".scopus_cookie.txt"


def _cookie() -> str:
    if not COOKIE_FILE.exists() or not COOKIE_FILE.read_text(encoding="utf-8").strip():
        raise RuntimeError(
            f"Scopus session cookie missing. Paste the browser Cookie header into {COOKIE_FILE}."
        )
    return COOKIE_FILE.read_text(encoding="utf-8").strip()


def _parse(raw: str) -> dict | None:
    raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip()).strip()
    try:
        return json.loads(raw)
    except ValueError:
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except ValueError:
            return None


def fetch_details(eid: str) -> dict | None:
    """Return the fields we keep from the Scopus gateway for one EID, or None on failure."""
    if not eid:
        return None
    api_key = config.require_env("FIRECRAWL_API_KEY")
    body = {
        "url": GATEWAY_URL.format(eid=eid),
        "formats": ["rawHtml"],
        "onlyMainContent": False,
        "headers": {
            "Cookie": _cookie(),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.scopus.com/",
        },
        "proxy": "enhanced",
        "actions": [{"type": "wait", "milliseconds": 3000}],
    }
    try:
        resp = requests.post(
            FIRECRAWL_SCRAPE_URL, json=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=180,
        )
        if resp.status_code != 200:
            return None
        data = _parse(resp.json().get("data", {}).get("rawHtml", "") or "")
    except requests.RequestException:
        return None
    if not data:
        return None

    abstract = data.get("abstract") or []
    return {
        "abstract": " ".join(abstract) if isinstance(abstract, list) else str(abstract),
        "authorKeywords": data.get("authorKeywords") or [],
        "openAccess": data.get("openAccess"),
        "language": data.get("language") or "",
        "publisher": (data.get("source") or {}).get("publisher", ""),
    }
