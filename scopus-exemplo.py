import argparse
# %% [markdown]
# ## 1. Import Dependencies

import json
import pandas as pd
import os
import re
import requests
import html
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from IPython.display import display

# %% [markdown]
# ## 2. Config Variables

TITLE = "Scopus"
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load_dotenv(path):
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass

# Load .env from the parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

SCOPUS_API_KEY = os.environ.get('SCOPUS_API_KEY', '')
SPRINGER_API_KEY = os.environ.get('SPRINGER_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
CROSSREF_EMAIL = os.environ.get('CROSSREF_EMAIL', '')

headers = {'Accept': 'application/json', 'X-ELS-APIKey': SCOPUS_API_KEY}
session = requests.Session()
# === Endpoints ===
SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'
SCOPUS_ABS_URL = 'https://api.elsevier.com/content/abstract/eid/{}'
CROSSREF_URL = 'https://api.crossref.org/works/{}'

# ("Code Generation" OR "Code Writer" OR "Software Development" OR "Code Completion") 
# AND ("Generative AI" OR "Generative Artificial Intelligence" OR "Generative Model*" OR "Large Language Model*" OR "Language Model*" OR "Small Language Model*" OR "LLM" OR "RAG" OR "Retrieval Augmented Generation" OR "Natural Language Processing" OR "NLP" OR "AI Agent" OR "LLM-based agent" OR "AI Multi-Agent" OR "Autonomous Agent") 
# AND ("Application" OR "Technolog*" OR "Approach*" OR "Method*" OR "Tool*" OR "Framework*" OR "Solution*" OR "Strateg*" OR "Model*" OR "Digital Solution*" OR "System*" OR "Platform*" OR "Technique*") 
# AND ("Software Engineering")

# TITLE-ABS-KEY(("Code Generation" OR "Code Writer" OR "Software Development" OR "Code Completion" OR "Debugging" OR "Program Repair" OR "Fault Localization" OR "Bug Detection" OR "Code Review" OR "Static Code Analysis" OR "Refactoring" OR "Code Restructuring" OR "Code Reorganization") 
# AND ("Generative AI" OR "Generative Artificial Intelligence" OR "Generative Model*" OR "Large Language Model*" OR "Language Model*" OR "Small Language Model*" OR "LLM" OR "RAG" OR "Retrieval Augmented Generation" OR "Natural Language Processing" OR "NLP" OR "AI Agent" OR "LLM-based agent" OR "AI Multi-Agent" OR "Autonomous Agent") 
# AND ("Application" OR "Technolog*" OR "Approach*" OR "Method*" OR "Tool*" OR "Framework*" OR "Solution*" OR "Strateg*" OR "Model*" OR "Digital Solution*" OR "System*" OR "Platform*" OR "Technique*") AND ("Software Engineering")) 
# AND PUBYEAR > 2021 AND PUBYEAR < 2026 AND ( LIMIT-TO ( SUBJAREA,"COMP" ) ) AND ( LIMIT-TO ( DOCTYPE,"ar" ) ) AND ( LIMIT-TO ( LANGUAGE,"English" ) )


# === Research String ===
# "Software Development",
POPULATION_ITEMS = ["Code Generation", "Code Writer", "Software Development", "Code Completion", 
                         "Debugging", "Program Repair", "Fault Localization", "Bug Detection",
                         "Code Review", "Static Code Analysis", 
                         "Refactoring", "Code Restructuring", "Code Reorganization"]

INTERVENTION_ITEMS = [
    "Generative AI", "Generative Artificial Intelligence", "Generative Model*",
    "Large Language Model*","Language Model*","Small Language Model*",
    "LLM", "RAG", "Retrieval Augmented Generation",
    "Natural Language Processing","NLP", "AI Agent", "LLM-based agent", "AI Multi-Agent",
    "Autonomous Agent"
]

OUTCOME_ITEMS = ["Application", "Technolog*", "Approach*", "Method*", "Tool*", "Framework*",
                 "Solution*", "Strateg*", "Model*", "Digital Solution*", "System*", "Platform*",
                 "Technique*"]

CONTEXT = "Software Engineering" 
START_YEAR = "2021"
END_YEAR = "2026"
SUBJAREA = "COMP"
DOCTYPE = "ar"
LANGUAGE = "English"

TOTAL_DOCUMENTS = 25
#TOTAL_DOCUMENTS = "ALL" #Se for igual a "ALL" retorna todos os documentos disponiveis na scopus, caso deseje retornar apenas os X primeiros, coloque um numero.

# Utilizado para webscraping e extrair parágrafos referentes aos documentos previamente retornados.
# OBS: A API gratuita do Scopus não retorna diretamente o abstract e, portanto, se faz necessário uma abordagem mais bruta para contornar essa limitação
MAX_PARAGRAPHS = 5


# %% [markdown]
# ## 3. Extract Scopus Metadata

import requests
import pandas as pd
import html
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from IPython.display import display

# === Configuration ===
# Build string

def step1_extract_metadata():
    population = " OR ".join(f'"{item}"' for item in POPULATION_ITEMS)
    intervention = " OR ".join(f'"{item}"' for item in INTERVENTION_ITEMS)
    outcome = " OR ".join(f'"{item}"' for item in OUTCOME_ITEMS)
        
    # Monta a research string para a tarefa utilizando os conectores lógicos AND e OR
    QUERY = f'TITLE-ABS-KEY(({population}) AND ({intervention}) AND ({outcome}) AND ("{CONTEXT}")) AND PUBYEAR > {START_YEAR} AND PUBYEAR < {END_YEAR} AND SUBJAREA({SUBJAREA}) AND (DOCTYPE({DOCTYPE})) AND LANGUAGE({LANGUAGE})'
    # OR DOCTYPE(cp)
    # TITLE-ABS-KEY( )
    
    COUNT = 25     # records per request (max 25)
    START = 0      # paging offset
    
    
    
    # === Fetch Scopus search results ===
    params = {'query': QUERY, 'count': COUNT, 'start': 0}
    resp = requests.get(SEARCH_URL, headers=headers, params=params)
    print("Scopus Query URL:", resp.url)
    resp.raise_for_status()
    info  = resp.json().get('search-results', {})
    
    import json
    os.makedirs(RESULTS_PATH, exist_ok=True)
    with open(os.path.join(RESULTS_PATH, "search-results.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)
        
    if (TOTAL_DOCUMENTS == "ALL"):
        total = int(info.get('opensearch:totalResults', 0))
    else:
        total = min(TOTAL_DOCUMENTS, int(info.get('opensearch:totalResults', 0)))
    
    print(f"Total records to fetch: {total}")
    
    records = []
    # Pagination
    for start in range(0, total, COUNT):
        print(f"Fetching records {start+1} to {min(start+COUNT, total)}...")
        r = requests.get(SEARCH_URL, headers=headers,
                         params={'query': QUERY, 'count': COUNT, 'start': start})
        r.raise_for_status()
        entries = r.json().get('search-results', {}).get('entry', [])
        if not entries:
            break
        for item in entries:
            title = item.get('dc:title', '')
            sid   = item.get('dc:identifier', '').replace('SCOPUS_ID:', '').replace('SCOPUS:', '')
            eid   = item.get('eid', '')
            doi   = item.get('prism:doi', '')
            doi_url = f"https://doi.org/{doi}" if doi else ''
            api_url = item.get('prism:url', '')
            lm = {li['@ref']: li['@href'] for li in item.get('link', []) if '@ref' in li and '@href' in li}
            preview_url = lm.get('scopus', '')
            records.append({
                'sid': sid,
                'eid': eid,
                'doi': doi,
                'doi_url': doi_url,
                'preview_url': preview_url,
                'api_url': api_url,
                'title': title,
                'authors': item.get('dc:creator',''),
                'publicationDate': item.get('prism:coverDate',''),
                'publicationVenue': item.get('prism:publicationName','')
            })
    
    # Garante existência do diretório (inclui todos os níveis de pasta)
    Path(RESULTS_PATH).mkdir(parents=True, exist_ok=True)
    
    # Cria DataFrame e exporta
    df_meta = pd.DataFrame(records)
    meta_csv = f'{TITLE}_meta.csv'
    df_meta.to_csv(f'{RESULTS_PATH}/{meta_csv}', index=False, encoding='utf-8')
    print(f"Metadata exported to {RESULTS_PATH}/{meta_csv}.")

# %% [markdown]
# ## 4. Extract Abstracts from Scopus

def step2_extract_abstracts():
    df_meta = pd.read_csv(f'{RESULTS_PATH}/{TITLE}_meta.csv')
    import random
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)…",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)…",
        # adicione outros exemplos…
    ]
    
    def random_headers():
        return {
            "User-Agent": random.choice(USER_AGENTS),
            # opcional: "Accept-Language", "Accept", etc.
        }
    
    def fetch_scopus_abstract(sid):
        """Try Scopus Abstract Retrieval API"""
        try:
            r = requests.get(SCOPUS_ABS_URL.format(sid), headers=headers, params={'view':'FULL'}, timeout=10)
            r.raise_for_status()
            ad = r.json().get('abstracts-retrieval-response', {})
            print('Successfully fetched directly from Scopus')
            return ad.get('coredata', {}).get('dc:description','') or ''
        except:
            print('Error fetching directly from Scopus')
            return ''
    
    
    def fetch_crossref_abstract(doi):
        """Try Crossref works API"""
        if not doi:
            return ''
        try:
            r = requests.get(CROSSREF_URL.format(doi), params={'mailto': CROSSREF_EMAIL}, timeout=10)
            r.raise_for_status()
            msg = r.json().get('message', {})
            raw = msg.get('abstract','')
            if raw:
                # strip XML/HTML tags
                print('Successfully fetched Crossref')
                return BeautifulSoup(raw, 'html.parser').get_text(separator=' ').strip()
        except:
            print('Error fetching from Crossref')
            return ''
        print('Error fetching from Crossref')
        return ''
    
    
    def scrape_html_paragraphs(url, title, max_par=MAX_PARAGRAPHS):
        """Fallback scraping of <p> tags or meta description"""
        try:
            hdr = random_headers()
            r = requests.get(url, headers=hdr, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
        except:
            print('Error scraping HTML')
            return []
        paras = []
        words = {w.lower() for w in re.findall(r"\w+", title) if len(w)>3}
        for p in soup.find_all('p'):
            txt = p.get_text(strip=True)
            if any(w in txt.lower() for w in words):
                paras.append(txt)
                if len(paras)>=max_par:
                    return paras
        # meta description
        meta = soup.find('meta',{'name':'description'}) or soup.find('meta',{'property':'og:description'})
        if meta and meta.get('content'):
            paras.append(meta['content'].strip())
    
        print('Successfully scraped HTML')
        return paras
    
    
    def fetch_abstract_from_doi_url(doi_url, title, max_par=3):
        """
        Segue redirecionamento de DOI e tenta extrair o abstract:
          1) meta[name="citation_abstract"]
          2) JSON-LD
          3) <div class="abstract author"> ou similares
          4) parágrafos filtrados pelo título
        """
        try:
            # segue redirect e obtém a página final
            r = session.get(doi_url, headers=random_headers(), timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
        except Exception:
            print("Erro ao acessar DOI URL")
            return ""
    
        # 1) meta da Elsevier / ScienceDirect
        meta_cit = soup.find('meta', attrs={'name': 'citation_abstract'})
        if meta_cit and meta_cit.get('content'):
            print("Sucesso: citation_abstract meta")
            return meta_cit['content'].strip()
    
        # 2) JSON-LD genérico
        jl = scrape_jsonld_abstract(soup)
        if jl:
            print("Sucesso: JSON-LD após DOI")
            return jl
    
        # 3) div do abstract (varia conforme template)
        div_abs = soup.find('div', class_='abstract author') or soup.find('div', class_='Abstracts')
        if div_abs:
            text = div_abs.get_text(" ", strip=True)
            if text:
                print("Sucesso: div.abstract")
                return text
    
        # 4) fallback em parágrafos relacionados ao título
        words = {w.lower() for w in re.findall(r"\w+", title) if len(w)>3}
        paras = []
        for p in soup.find_all('p'):
            txt = p.get_text(strip=True)
            if any(w in txt.lower() for w in words):
                paras.append(txt)
                if len(paras) >= max_par:
                    break
        if paras:
            print("Sucesso: parágrafos filtrados após DOI")
            return " ".join(paras)
    
        print("Nenhum abstract encontrado na landing page DOI")
        return ""
    
    
    # --- 1) Content negotiation via DOI (CSL-JSON) ---
    def fetch_csl_abstract(doi):
        """
        Pede ao doi.org conteúdo em CSL-JSON (muitos publishers retornam 'abstract').
        """
        if not doi:
            return ''
        url = f'https://doi.org/{doi}'
        headers = {
            'Accept': 'application/vnd.citationstyles.csl+json',
            # rotacione UA se quiser
        }
        try:
            r = session.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            abs_ = data.get('abstract','')
            if abs_:
                print("Sucesso: CSL-JSON via DOI")
                return abs_
        except Exception:
            print("Erro: CSL-JSON via DOI")
        print("Erro: CSL-JSON via DOI")
        return ''
    
    # --- 2) OpenAlex API ---
    def fetch_openalex_abstract(doi):
        """
        Usa OpenAlex para metadados: reconstrói o abstract a partir de
        abstract_inverted_index.
        """
        if not doi:
            return ''
        url = f'https://api.openalex.org/works/doi:{doi}'
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            idx = data.get('abstract_inverted_index', {})
            if idx:
                # reconstrói posição→palavra
                n = max(pos for poses in idx.values() for pos in poses) + 1
                tokens = [''] * n
                for word, poses in idx.items():
                    for p in poses:
                        tokens[p] = word
                abstract = ' '.join(tokens).strip()
                print("Sucesso: OpenAlex")
                return abstract
        except Exception:
            print("Erro: OpenAlex")
        print("Erro: OpenAlex")
        return ''
    
    # --- 3) Europe PMC (só artigos indexados em PMC) ---
    def fetch_epmc_abstract(doi):
        """
        Query à Europe PMC: devolve 'abstractText' se existir.
        """
        if not doi:
            return ''
        url = (
            'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
            '?query=DOI:{}&format=json'
        ).format(doi)
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
            res = r.json().get('resultList',{}).get('result',[])
            if res and res[0].get('abstractText'):
                print("Sucesso: Europe PMC")
                return res[0]['abstractText'].strip()
        except Exception:
            print("Erro: Europe PMC")
        print("Erro: Europe PMC")
        return ''
    
    
    def fetch_springer_api(doi):
        """
        Usa Metadata API da Springer Nature para obter abstract.
        Cadastre-se e pegue uma API key em https://dev.springernature.com/.
        """
        url = f'http://api.springernature.com/metadata/json/doi/{doi}'
        params = {'api_key': SPRINGER_API_KEY}
        try:
            r = session.get(url, params=params, timeout=10)
            r.raise_for_status()
            recs = r.json().get('records', [])
            if recs and recs[0].get('abstract'):
                print("Sucesso: Springer API")
                return recs[0]['abstract'].strip()
        except Exception as e:
            print("Erro: Springer API")
        print("Erro: Springer API")
        return ''
    
    
    def fetch_sciencedirect_abstract(identifier):
        """
        Usa a Article Retrieval API da Elsevier para obter o abstract de
        um artigo ScienceDirect, a partir de DOI ou PII.
        Pré-requisito: ter sua chave em ELSEVIER_API_KEY.
        """
        # Determina se veio DOI (começa com "10.") ou PII (caso contrário)
        if identifier.startswith("10."):
            endpoint = "doi"
        else:
            endpoint = "pii"
        url = f"https://api.elsevier.com/content/article/{endpoint}/{identifier}"
        headers = {
            "X-ELS-APIKey": SCOPUS_API_KEY,
            "Accept": "application/json"
        }
        params = {"view": "FULL"}
        try:
            r = session.get(url, headers=headers, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            core = data.get("full-text-retrieval-response", {}) \
                       .get("coredata", {})
            abstract = core.get("dc:description", "").strip()
            if abstract:
                print("Sucesso: ScienceDirect API")
                return abstract
        except Exception as e:
            print("Erro: ScienceDirect API", e)
        return ""
    
    # === Aggregate abstracts ===
    abstracts = []
    for idx, row in df_meta.iterrows():
        print(f"{idx}. Extraindo abstract: {row['title']}")
        text = (
            fetch_scopus_abstract(row['sid'])
            or fetch_crossref_abstract(row['doi'])
            or fetch_s2_abstract(row['doi'])
            or fetch_csl_abstract(row['doi'])
            or fetch_openalex_abstract(row['doi'])
            or fetch_epmc_abstract(row['doi'])
        )
        # ScienceDirect
        if not text and row.get('doi_url'):
            text = fetch_sciencedirect_abstract(row['doi'])
            
        if not text and row.get("preview_url"):
            text = scrape_html_paragraphs(row["preview_url"], row["title"])
            text = " ".join(text)
            
        if not text and row.get("doi_url"):
            text = fetch_abstract_from_doi_url(row["doi_url"], row["title"])
            
        if not text and row.get("preview_url"):
            text = scrape_with_selenium(row["preview_url"])
            
        # SpringerLink
        if not text and row.get('doi_url'):
            text = fetch_springer_api(row['doi'])
    
        abstracts.append(text or "")
        print("-" * 60)
    
    df_meta['abstract_fetched'] = abstracts
    
    display(df_meta[['sid','doi','preview_url','abstract_fetched']])
    
    df_meta.to_csv(f'{RESULTS_PATH}/{TITLE}_abstracts.csv', index=False)

# %% [markdown]
# ## 5. Analyze Documents Title & Abstract using LLM

# %% [markdown]
# ### 5.1 Define Prompt

import json
import textwrap

def step3_analyze_documents():
    prompt = textwrap.dedent("""\
        Role: You are a software engineering researcher working on the following research:
    
        Research Info:
        Title: Generative Artificial Intelligence-based solutions Applicable to Software Engineering: An Overview for Industry and Academia
    
        Context: Some concepts have recently emerged in technology, giving rise to new paradigms and challenges for developing systems and software. One of these concepts is Artificial Intelligence (AI). Although it is not a recent concept, the availability of technological solutions, data, and processing capacity has made AI a tool that allows individuals to enhance their ability to perform their daily tasks. Among the set of tasks, contemporary software systems engineering, focusing on the Internet of Things (IoT), is based on narrowing the gap between the real and virtual worlds. Its emergence emerged from initiatives aimed at remotely tracking objects containing electronic tags (RFID electronic tags) that can be read at greater distances than conventional ones (barcodes). Subsequently, sensor technologies emerged and further spread the possibilities of perceiving the physical environment around us, collecting information on temperature, proximity, humidity, brightness, noise, etc. In addition to perception, it became possible to trigger mechanical actions in the physical environment through actuators. However, constructing these systems involves a set of clerical tasks in the different life cycle phases, for which AI technologies could bring competitive and productive performance advantages.
    
        Motivation: Much has been observed regarding the support of AI tools for generating and evaluating source code. However, although important, coding represents a small percentage of engineering activities throughout the life cycle. Therefore, it is necessary to observe the other activities in the life cycle, for which there is still no clarity about the risks and challenges of using AI tools when performing them. Exploring these tools offers valuable insights into how AI tools can enhance Software Engineering practices and contribute to advancing research in the field.
    
        Problem: To evolve the software engineering activities by integrating Generative AI tools in the constructive process.
    
        Objective: To identify and map the Artificial Intelligence (AI)-based solutions available to support Software Engineering activities, focusing on industry and academic contexts. Organize the findings into a comprehensive catalog by analyzing their applicability, accessibility, usage models, and limitations. Besides, to observe the use of some of these AI-based tools in developing contemporary software systems projects.
    
        Tasks of Interest: AI in Coding, Debugging, and Code Review: AI in code generation: programming copilots and intelligent assistants; Automated debugging with AI: bug detection and code optimization; Static analysis and code review with AI; Automatic code refactoring and performance improvement.
    
        Research question:
        1) Which Generative Artificial Intelligence-based solutions (tools, agents, models, etc.) are available to support Software Engineering activities, considering the contexts of industry and academia?
        a) Where can these solutions be found?
        b) How can these solutions be used?
        c) What is the access and usage model for these solutions and costs?
        d) What limitations must be considered for adopting these solutions?
        e) What is the maturity level of these solutions?
        f) Is there technical documentation, support, or an active community to facilitate these solutions in academia and industry?
        g) What types of target users or roles typically engage with the proposed solutions? (e.g., requirements engineers, testers, developers)
        h) Is there any collaboration with the industry to validate the proposals through case studies or experiments?
    
    
        !Attention: We are interested mostly in tools, agents, models, etc that support Software Engineering activities, be rigorous when evaluating the papers.
    
        For each Title, evaluate and format the answer exactly as the following JSON structure, be thoughtful and rigorous about each response, elaborating it if applicable if given context,
        answering all the ICs, ECs and RQs :
        {
          "IC1": "<Primary source must be in the context of software engineering;>",
          "IC2": "<Primary source must present a solution generative AI applicable to <SE thematic interest>;>",
          "IC3": "<Primary source must report a primary study or a case of application in the field;>",
          "IC4": "<Primary source must report a deployed solution that can be used in the industry;>",
          "IC6": "<Primary Source must provide data to answer at least one of the RMR research questions;>",
          "EC1": "<Primary source does not meet at least one IC;>",
          "EC2": "<Duplicate primary sources;>",
          "EC3": "<Primary source is unavailable for free download or through institutional access;>",
          "EC4": "<Primary source written in languages other than English unless official translations are available;>",
          "EC5": "<Primary source is a secondary study;>",
          "RQ1a": "<indicate links to the channels or platforms where the tools are available>>",
          "RQ1b": "<indicate type of tool and context of use>",
          "RQ1c": "<Provide licensing/authentication/cost info>",
          "RQ1d": "<Indicate technical, operational, legal/ethical constraints>",
          "RQ1e": "<Indicate maturity (experimental/beta/production)>",
          "RQ1f": "<Indicate available documentation/support channels>",
          "RQ1g": "<Indicate specific target roles>",
          "RQ1h": "<Indicate case-study or experiment evidence>",
          "Final Decision": "<Include or Exclude>"
          "Final Decision Rating": "<In a scale from 0 to 100%, how likely is this evaluation likely to be correct -> if study should be excluded or not>".
          "Final Decision Reasoning": <"Explain why you decided to include or exclude, following the criteria defined previously>".
        }
    
        (Do not add any other keys; respond only with valid JSON.)
        """)
    
    payload = {
        "role": "system",
        "content": prompt
    }
    
    import os
    import time
    import pandas as pd
    import openai
    
    # 1. Configure your OpenAI API key
    openai.api_key = OPENAI_API_KEY
    OUTPUT_SUFFIX = "evaluated"
    
    df = pd.read_csv(os.path.join(RESULTS_PATH, f'{TITLE}_abstracts.csv'))
    
    #=============================================================
    ## Filter rows with abastracts (OPTIONAL) // 
    #=============================================================
    df = df.dropna(subset=['abstract_fetched'])
    df.reset_index(inplace=True, drop=True)
    
    
    evaluations = []
    abstracts   = []
    
    counter = 0
    for title, abstract in zip(df["title"].fillna(""), df["abstract_fetched"].fillna("")):
        print(f'{counter}. {title}')
        print(abstract)
        print("\n======================================\n")
        counter+=1
        user_msg = {
            "role": "user",
            "content": (
                f"Here is the website summary as extracted:\n\n{abstract}\n\n"
                f"Now, evaluate the following title in the given context, answering all ICs, ECs and RQs previously defined in a thoughtful way:\n\"{title.strip()}\""
            )
        }
        
        try:
            # gpt-4 provides good answers but is expensive
            # 
            resp = openai.chat.completions.create(
                model="gpt-4.1", #GPT-4o mini
                messages=[payload, user_msg],
                temperature=0.2,
            )
            reply = resp.choices[0].message.content.strip()
        except Exception as e:
            reply = f'{{"error":"{str(e)}"}}'
    
        evaluations.append(reply)
        time.sleep(1)
    
    # 6. Save back to CSV with both evaluation and abstract
    df["evaluation"] = evaluations
    out_path = os.path.join(
        RESULTS_PATH,
        f"{TITLE}_abstracts_{OUTPUT_SUFFIX}.csv"
    )
    df.to_csv(out_path, index=False)
    print(f"→ Saved evaluated results to {out_path}")
    print("\n========================================\n")


# %% [markdown]
# ## 6. Generate Latex Tables

# import json
# import pandas as pd
# import os
# import re
# from urllib.parse import urlparse

def step4_generate_latex():
    def sanitize(text: str) -> str:
        s = str(text or "")
        s = re.sub(r'[\x00-\x1F\x7F]', '', s)
        return s.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    
    def escape_latex(text: str) -> str:
        t = sanitize(text)
        return (t
                .replace("\\", r"\textbackslash{}")
                .replace("&", r"\&")
                .replace("%", r"\%")
                .replace("$", r"\$")
                .replace("#", r"\#")
                .replace("_", r"\_")
                .replace("{", r"\{")
                .replace("}", r"\}")
                .replace("~", r"\textasciitilde{}")
                .replace("^", r"\^{}"))
    
    def extract_date(snippet: str) -> str:
        return sanitize(snippet).split("...")[0].strip()
    
    def extract_domain(link: str, fallback: str) -> str:
        """
        Tenta extrair o domínio de uma URL.
        Se falhar, retorna `fallback`.
        """
        try:
            netloc = urlparse(link).netloc
            # remove porta ou credenciais se existir
            return netloc.split('@')[-1].split(':')[0] or fallback
        except:
            return fallback
    
    
    def format_abstract(text: str) -> str:
        # 1) garante string e limpa caracteres de controle
        s = sanitize(text)
        # 2) troca quebras de linha por espaço e colapsa múltiplos espaços
        s = re.sub(r'\s+', ' ', s).strip()
        # 3) remove um eventual prefixo "Abstract" ou "ABSTRACT:" no início
        s = re.sub(r'^(abstract[:\s]*)', '', s, flags=re.IGNORECASE)
        # 4) escape LaTeX nos caracteres especiais
        s_esc = escape_latex(s)
        # 5) envolve em itálico
        return r"\emph{" + s_esc + "}"
    
    
    def generate_variant(df, subtitle, output_file, show_final_fields=True):
        """
        Gera um .tex com tabelas breakables (longtable):
          - Usa snippet→Year
          - Source = domínio(link) ou subtitle
          - Duas variantes: com/sem Rating+Reasoning
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        lines = []
        a_count, r_count = 1, 1
    
        # separar incluídos e excluídos
        entries = []
        for _, row in df.iterrows():
            try:
                ev = json.loads(row["evaluation"])
            except:
                continue
            decision = ev.get("Final Decision","").strip().lower()
            entries.append((row, ev, decision=="include"))
        included = [e for e in entries if e[2]]
        rejected = [e for e in entries if not e[2]]
    
        def render(row, ev, is_inc, idx):
            color        = "blue!20" if is_inc else "red!20"
            header_color = "blue!40" if is_inc else "red!40"
            tag          = f"A{idx}" if is_inc else f"R{idx}"
            cap_label    = f"{subtitle} {tag}"
            wid          = escape_latex(row.get("id",""))
            date_str     = extract_date(row.get("snippet",""))
            # domínio ou subtitle
            src = extract_domain(row.get("link",""), subtitle)
    
            # início do longtable
            lines.append(
                r"\begin{longtable}{|>{\columncolor{" + color + r"}}l|p{0.65\textwidth}|}"
            )
            lines.append(r"\caption{" + cap_label + " --- " + wid + r"} \\ \hline")
            lines.append(r"\rowcolor{" + header_color + r"}")
            lines.append(
                r"\multicolumn{2}{|l|}{\textbf{" + cap_label + " -- " + wid + r"}} \\ \hline"
            )
    
            # metadados
            meta = [
                ("Title",     escape_latex(row.get("title",""))),
                ("Link",      escape_latex(row.get("doi_url",""))),
                ("Author(s)", escape_latex(row.get("authors",""))),
                ("Source" ,   escape_latex(row.get("publicationVenue",""))),
                ("Year",      escape_latex(row.get("publicationDate",""))),
                ("Abstract",  format_abstract(row.get("abstract_fetched",""))),
            ]
            for k,v in meta:
                lines.append(f"{k} & {v} \\\\ \\hline")
    
            # Technologies
            lines.append(
                f"Technologies & {escape_latex(ev.get('Technologies',''))} \\\\ \\hline"
            )
    
            # IC*, EC*, RQ1[a-h]
            for pat in (r"IC\d+", r"EC\d+", r"RQ1[a-h]"):
                for key in sorted(k for k in ev if re.match(pat, k)):
                    lines.append(f"{key} & {escape_latex(ev[key])} \\\\ \\hline")
    
            # Final Decision
            lines.append(
                f"Final Decision & {escape_latex(ev.get('Final Decision',''))} \\\\ \\hline"
            )
            if show_final_fields:
                for fld in ("Final Decision Rating","Final Decision Reasoning"):
                    if fld in ev:
                        lines.append(f"{fld} & {escape_latex(ev[fld])} \\\\ \\hline")
    
            # fim do longtable
            lines.append(r"\end{longtable}")
            lines.append("")
    
        # renderiza incluídos primeiro
        for row,ev,_ in included:
            render(row, ev, True, a_count)
            a_count += 1
        # depois excluídos
        for row,ev,_ in rejected:
            render(row, ev, False, r_count)
            r_count += 1
    
        # grava resultado
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  -> {output_file}")
    
    
        df = pd.read_csv(
            f"{RESULTS_PATH}/{TITLE}_abstracts_evaluated.csv"
        )
        # Full (com Rating+Reasoning)
        generate_variant(df,
                         subtitle=TITLE,
                         output_file=f'{RESULTS_PATH}/latex_tables/{TITLE}/all_tables_full.tex',
                         show_final_fields=True)
        # Simple (sem Rating+Reasoning)
        generate_variant(df,
                         subtitle=TITLE,
                         output_file=f'{RESULTS_PATH}/latex_tables/{TITLE}/all_tables_simple.tex',
                         show_final_fields=False)

def main():
    parser = argparse.ArgumentParser(description="Pipeline Scopus")
    parser.add_argument("--step", type=str, default="all", choices=["1", "2", "3", "4", "all"], help="Passo a ser executado (1: Metadados, 2: Abstracts, 3: IA, 4: Tabelas)")
    args = parser.parse_args()

    if args.step in ["1", "all"]:
        print("\n=== PASSO 1: Extraindo Metadados ===")
        step1_extract_metadata()
    if args.step in ["2", "all"]:
        print("\n=== PASSO 2: Extraindo Abstracts ===")
        step2_extract_abstracts()
    if args.step in ["3", "all"]:
        print("\n=== PASSO 3: Analisando Documentos ===")
        step3_analyze_documents()
    if args.step in ["4", "all"]:
        print("\n=== PASSO 4: Gerando Tabelas ===")
        step4_generate_latex()

if __name__ == "__main__":
    main()
