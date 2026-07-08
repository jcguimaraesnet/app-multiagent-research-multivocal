"""Grey-literature content acquisition: scrape a page to markdown via Firecrawl."""

import requests

from rmr import config

SCRAPE_URL = "https://api.firecrawl.dev/v2/scrape"


def scrape_markdown(url: str) -> str | None:
    """Return the page's main content as markdown, or None if it cannot be retrieved."""
    if not url:
        return None
    api_key = config.require_env("FIRECRAWL_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"url": url, "formats": ["markdown"], "onlyMainContent": True}
    try:
        resp = requests.post(SCRAPE_URL, json=body, headers=headers, timeout=180)
        if resp.status_code != 200:
            return None
        return (resp.json().get("data", {}).get("markdown") or "").strip() or None
    except requests.RequestException:
        return None
