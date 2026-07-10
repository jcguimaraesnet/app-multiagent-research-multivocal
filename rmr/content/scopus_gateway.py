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

# A real gateway response is a JSON document carrying at least one of these keys. A login /
# redirect page (served when the session cookie is stale) does not, which is how we tell an
# expired cookie apart from a genuinely empty document.
_DOCUMENT_KEYS = ("abstract", "authorKeywords", "openAccess", "source")


class ScopusAuthError(RuntimeError):
    """The Scopus gateway did not return document data, most likely because the session
    cookie is missing or expired (it served a login/redirect page instead of the JSON)."""


def _cookie() -> str:
    if not COOKIE_FILE.exists() or not COOKIE_FILE.read_text(encoding="utf-8").strip():
        raise ScopusAuthError(
            f"Scopus session cookie missing. Paste the browser Cookie header into {COOKIE_FILE}."
        )
    return COOKIE_FILE.read_text(encoding="utf-8").strip()


def _is_document(data: dict) -> bool:
    return isinstance(data, dict) and any(key in data for key in _DOCUMENT_KEYS)


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
        raw = resp.json().get("data", {}).get("rawHtml", "") or ""
    except requests.RequestException:
        return None
    if not raw.strip():
        return None  # empty response: transient proxy/gateway hiccup, retry later

    data = _parse(raw)
    if not _is_document(data or {}):
        # Non-empty response that is not the document JSON: the gateway served a login/redirect
        # page, so the session cookie is stale. Fail loudly instead of writing empty content.
        raise ScopusAuthError(
            "Scopus gateway returned no document data for "
            f"eid={eid!r}; the session cookie in {COOKIE_FILE} is most likely expired. "
            "Refresh it from a logged-in browser session (copy the Cookie header) and re-run "
            "the scrape substep. If the cookie is fresh, the gateway may have returned an "
            "unexpected response for this EID."
        )

    abstract = data.get("abstract") or []
    return {
        "abstract": " ".join(abstract) if isinstance(abstract, list) else str(abstract),
        "authorKeywords": data.get("authorKeywords") or [],
        "openAccess": data.get("openAccess"),
        "language": data.get("language") or "",
        "publisher": (data.get("source") or {}).get("publisher", ""),
    }
