"""Full-title recovery for grey web results (Google, GitHub).

Firecrawl's search endpoint returns Google's snippet title, which is truncated with an
ellipsis. The full title lives in the page's `og:title`/`<title>`. This module recovers it
with a free HTTP GET first (works for GitHub and most blogs), falling back to a Firecrawl
scrape only for pages behind anti-bot protection (Cloudflare/JS challenges), where the
enhanced proxy is needed. It does not use the OpenAI Agents SDK.
"""

import re
import time
from html import unescape

import requests

from rmr import config

SCRAPE_URL = "https://api.firecrawl.dev/v2/scrape"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# Interstitial titles served by anti-bot layers instead of the real page title.
BLOCKED_MARKERS = (
    "just a moment", "verifying your browser", "attention required",
    "access denied", "please enable javascript", "are you a robot",
    "checking your browser",
)


def _is_truncated(title: str) -> bool:
    """A search-snippet title cut off by the engine ends with an ellipsis."""
    t = (title or "").rstrip()
    return t.endswith("...") or t.endswith("…") or "…" in t


def _looks_blocked(title: str) -> bool:
    t = (title or "").strip().lower()
    return (not t) or t == "error" or any(m in t for m in BLOCKED_MARKERS)


def _extract_title(html: str) -> str:
    """Prefer og:title (order-independent), fall back to the <title> element."""
    for match in re.finditer(r"<meta\b[^>]*>", html, re.I):
        tag = match.group(0)
        if re.search(r"(property|name)\s*=\s*[\"']og:title[\"']", tag, re.I):
            content = re.search(r"content\s*=\s*[\"']([^\"']*)[\"']", tag, re.I)
            if content and content.group(1).strip():
                return unescape(" ".join(content.group(1).split()))
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return unescape(" ".join(title.group(1).split())) if title else ""


def _free_title(url: str) -> str:
    """Full title via a plain GET, or "" if it cannot be retrieved / is blocked."""
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=15, allow_redirects=True)
        if resp.status_code != 200:
            return ""
        return _extract_title(resp.text[:200000])
    except requests.RequestException:
        return ""


def _firecrawl_title(url: str) -> str:
    """Full title via Firecrawl scrape metadata (enhanced proxy defeats anti-bot)."""
    api_key = config.require_env("FIRECRAWL_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"url": url, "formats": ["markdown"], "onlyMainContent": True, "proxy": "auto"}
    try:
        resp = requests.post(SCRAPE_URL, json=body, headers=headers, timeout=180)
        if resp.status_code != 200:
            return ""
        meta = resp.json().get("data", {}).get("metadata", {}) or {}
    except requests.RequestException:
        return ""
    for key in ("ogTitle", "title"):
        value = meta.get(key)
        if isinstance(value, list):
            value = value[0] if value else ""
        if value and str(value).strip():
            return " ".join(str(value).split())
    return ""


def fetch_titles(records: list[dict]) -> dict[str, str]:
    """Recover full titles for records whose snippet title is truncated.

    Returns {id: full_title}. Free GET first; Firecrawl only for pages the GET could not
    retrieve or that returned an anti-bot interstitial. Records with a complete title (no
    ellipsis) are skipped.
    """
    result: dict[str, str] = {}
    free_ok = fc_used = fc_ok = 0
    targets = [r for r in records if _is_truncated(r.get("title", ""))]
    print(f"[titles] recovering {len(targets)} truncated titles...")
    for i, record in enumerate(targets, start=1):
        rid = record["id"]
        url = record.get("link", "")
        title = _free_title(url)
        if title and not _looks_blocked(title):
            result[rid] = title
            free_ok += 1
            print(f"[titles] {i}/{len(targets)} {rid}: free GET ok")
            time.sleep(0.2)
            continue
        fc_used += 1
        title = _firecrawl_title(url)
        if title and not _looks_blocked(title):
            result[rid] = title
            fc_ok += 1
            print(f"[titles] {i}/{len(targets)} {rid}: firecrawl fallback ok")
        else:
            print(f"[titles] {i}/{len(targets)} {rid}: not recovered (kept truncated)")
        time.sleep(0.5)
    print(f"[titles] {len(targets)} truncated: {free_ok} via free GET, "
          f"{fc_ok}/{fc_used} via Firecrawl fallback ({len(result)} recovered)")
    return result
