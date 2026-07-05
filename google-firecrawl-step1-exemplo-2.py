#!/usr/bin/env python3
"""
Reproducao da metodologia PICO do notebook (Extract Data Github & PapersWithCode3.ipynb),
agora no Firecrawl /v2/search.

Estrutura original:
  research_string = (POPULATION_da_tarefa) AND (INTERVENTION) AND (OUTCOME) AND ("Software Engineering")
  para cada tarefa x cada filtro (web inteira / site:github.com / site:paperswithcode.com)

Aqui: 'site:' vai na query (no lugar dos CX) e a data via parametro tbs.
Saida: Data_firecrawl/<task>_<alvo>.csv  +  results_pico_all.csv (uniao deduplicada).
"""
import os, csv, sys, time, requests

# modo sem wildcards: remove o '*' final dos termos (ex.: "Model*" -> "Model")
NO_WILDCARD = "--no-wildcard" in sys.argv

def load_dotenv(path=".env"):
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_dotenv()
API_KEY = os.environ["FIRECRAWL_API_KEY"]

# --- PICO (identico a celula 8 do notebook) ---
task_population_dict = {
    "Code Generation": ["Code Generation", "Code Writer", "Software Development", "Code Completion"],
    "Program Repair": ["Debugging", "Program Repair", "Fault Localization", "Bug Detection"],
    "Code Review": ["Code Review", "Static Code Analysis"],
    "Refactor": ["Refactoring", "Code Restructuring", "Code Reorganization"],
}
task_population_dict["All"] = (task_population_dict["Code Generation"] + task_population_dict["Program Repair"]
                               + task_population_dict["Code Review"] + task_population_dict["Refactor"])

intervention_items = [
    "Generative AI", "Generative Artificial Intelligence", "Generative Model*",
    "Large Language Model*", "Language Model*", "Small Language Model*",
    "LLM", "RAG", "Retrieval Augmented Generation",
    "Natural Language Processing", "NLP", "AI Agent", "LLM-based agent", "AI Multi-Agent",
    "Autonomous Agent",
]
outcome_items = ["Application", "Technolog*", "Approach*", "Method*", "Tool*", "Framework*",
                 "Solution*", "Strateg*", "Model*", "Digital Solution*", "System*", "Platform*",
                 "Technique*"]

def grp(items):
    cleaned = [(i[:-1].strip() if NO_WILDCARD and i.endswith("*") else i) for i in items]
    # dedup preservando ordem (apos remover '*' pode haver repetidos)
    seen, out = set(), []
    for i in cleaned:
        if i not in seen:
            seen.add(i); out.append(i)
    return " OR ".join(f'"{i}"' for i in out)
INTERVENTION = grp(intervention_items)
OUTCOME = grp(outcome_items)

# Filtros (equivalente aos 3 CX). label -> operador site: (vazio = web inteira)
FILTERS = {"web": "", "github.com": "site:github.com", "paperswithcode.com": "site:paperswithcode.com"}

# Data: "after December 2021" -> jan/2022 ; ate 2025
TBS = "cdr:1,cd_min:1/1/2022,cd_max:12/31/2025"
PER_CALL = 100
COUNTRY = "US"
OUTDIR = "Data_firecrawl_nowild" if NO_WILDCARD else "Data_firecrawl"
UNION_CSV = "results_pico_all_nowild.csv" if NO_WILDCARD else "results_pico_all.csv"


def search(query):
    body = {"query": query, "limit": PER_CALL, "tbs": TBS,
            "sources": [{"type": "web"}], "country": COUNTRY}
    r = requests.post("https://api.firecrawl.dev/v2/search", json=body,
                      headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                      timeout=180)
    if r.status_code != 200:
        print(f"    HTTP {r.status_code}: {r.text[:160]}")
        return []
    return r.json().get("data", {}).get("web", [])


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    union = {}  # link -> (task, filtro, title)
    summary = []
    for task, pop in task_population_dict.items():
        research = f"({grp(pop)}) AND ({INTERVENTION}) AND ({OUTCOME}) AND (\"Software Engineering\")"
        for label, op in FILTERS.items():
            query = f"{research} {op}".strip()
            print(f"Tarefa: {task:16} | alvo: {label}")
            items = search(query)
            seen, rows = set(), []
            for it in items:
                u = it.get("url", "")
                if u and u not in seen:
                    seen.add(u)
                    rows.append((it.get("title", ""), u))
                    union.setdefault(u, (task, label, it.get("title", "")))
            path = os.path.join(OUTDIR, f"{task}_{label}.csv")
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["title", "link"]); w.writerows(rows)
            print(f"    {len(rows):3} unicos -> {path}")
            summary.append((task, label, len(rows)))
            time.sleep(1)

    with open(UNION_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["task", "filter", "title", "link"])
        for u, (task, label, title) in union.items():
            w.writerow([task, label, title, u])

    print("\n=== RESUMO ===")
    for task, label, n in summary:
        print(f"  {task:16} {label:18} {n}")
    print(f"\nUniao deduplicada: {len(union)} links unicos -> {UNION_CSV}")


if __name__ == "__main__":
    main()
