#!/usr/bin/env python3
"""
Firecrawl Search -> results_step1.csv (title + link)

Credencial lida do .env:
  FIRECRAWL_API_KEY=fc-...

Uso:
  python3 search_step1_firecrawl.py
"""
import csv
import os
import sys
import requests


def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()
API_KEY = os.environ.get("FIRECRAWL_API_KEY", "").strip()

# --- String de busca (achatada em uma linha) ---
QUERY = (
    '("Code Generation" OR "Code Writer" OR "Code Completion" OR "Code Evolution" '
    'OR "Refactoring" OR "Code Restructuring" OR "Code Reorganization" '
    'OR "Program Generation" OR "Program Writer" OR "Program Completion" '
    'OR "Program Evolution") AND ("Generative AI" OR "Generative Model" '
    'OR "Large Language Model" OR "Retrieval Augmented Generation" OR "NLP" '
    'OR "Machine Learning")'
)

# --- Filtros de data ---
# (1) after December 2021 -> cd_min 1/1/2022 (a partir de jan/2022)
# (2) up to the search execution in 2025 -> cd_max 12/31/2025
TBS = "cdr:1,cd_min:1/1/2022,cd_max:12/31/2025"

ENDPOINT = "https://api.firecrawl.dev/v2/search"
OUTPUT = "results_step1.csv"
TARGET = 100          # numero de links UNICOS desejados
PER_CALL = 100        # teto do Firecrawl por chamada

# Busca web principal (EUA) e, se faltar para 100 unicos, completa com outras regioes.
SEARCH_PLAN = [
    {"country": "US"},
    {"country": "GB"},
    {"country": "CA"},
    {"country": "AU"},
]


def search(country):
    body = {
        "query": QUERY,
        "limit": PER_CALL,
        "tbs": TBS,
        "sources": [{"type": "web"}],
        "country": country,
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    r = requests.post(ENDPOINT, json=body, headers=headers, timeout=180)
    if r.status_code != 200:
        print(f"  aviso: HTTP {r.status_code} ({country}): {r.text[:200]}")
        return []
    return r.json().get("data", {}).get("web", [])


def main():
    if not API_KEY:
        sys.exit("ERRO: defina FIRECRAWL_API_KEY no .env (ex.: FIRECRAWL_API_KEY=fc-...)")

    seen = set()
    rows = []  # (title, link)
    for step in SEARCH_PLAN:
        if len(rows) >= TARGET:
            break
        country = step["country"]
        print(f"Buscando web/{country} (tbs={TBS}) ...")
        for it in search(country):
            url = it.get("url", "")
            if url and url not in seen:
                seen.add(url)
                rows.append((it.get("title", ""), url))
                if len(rows) >= TARGET:
                    break
        print(f"  unicos acumulados: {len(rows)}")

    rows = rows[:TARGET]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["title", "link"])
        w.writerows(rows)

    print(f"\nGravado {len(rows)} links unicos em {OUTPUT}")
    if len(rows) < TARGET:
        print(f"ATENCAO: so foi possivel obter {len(rows)} (<{TARGET}) links unicos.")


if __name__ == "__main__":
    main()
