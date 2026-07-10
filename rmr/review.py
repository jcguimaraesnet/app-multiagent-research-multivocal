"""Step 5: export blind human-review spreadsheets (one .xlsx per screening step).

For the census dual-review design, every item the LLM screened at steps 2, 3 and 4 is listed
for an independent, BLIND human reviewer. The ``decision`` column is left EMPTY (an
Include/Exclude dropdown) so the reviewer is not anchored by the LLM verdict; the LLM decision
stays in the step JSON files and is joined back by ``id`` when the review is scored later.

Each sheet aggregates all origins into one workbook; the ``id`` keeps its origin prefix
(SC / GO / GH / HF), so the origin is always recoverable. This reads only the step outputs and
the captured-content files, so it needs no LLM call.

Sheets (``data/review/<MODEL_EXPERIMENT>/``):
- ``step-2-review.xlsx``: id, title, decision.
- ``step-3-review.xlsx``: id, abstract, keywords, decision. For grey literature the ``abstract``
  cell composes the abstract/summary with its publication date and link.
- ``step-4-review.xlsx``: id, title, file, decision. ``file`` is the source document name (the
  PDF for scopus/hf, the scraped Markdown for google/github).
"""

import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from rmr import config
from rmr.paths import (abstract_path, ensure_parent, full_path, pdf_path,
                       review_dir, step_output_path)

ORIGINS = ["scopus", "google", "github", "hf"]
# Origins whose step-3 content is an LLM summary of a web page: for these the abstract cell
# composes the summary with its publication date and link. scopus and hf carry a real abstract
# (Scopus gateway / arXiv), so they go in as-is. Mirrors GREY_SUMMARY_ORIGINS in screening.
COMPOSE_ORIGINS = {"google", "github"}
DECISION_VALUES = '"Include,Exclude"'  # Excel list-validation formula for the decision column
AGREEMENT_VALUES = '"Yes,No"'          # ... for the answers-review agreement column
RQ_KEYS = ["RQa", "RQb", "RQc", "RQd", "RQe", "RQf", "RQg", "RQh"]


def _records(origin: str, step: int) -> list[dict] | None:
    """The step's screened records for one origin, or None when the step has not run there."""
    path = step_output_path(origin, step)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("records", [])


def _captured(origin: str, item_id: str) -> dict:
    """The captured/summarized content for one item (content/abstract/<id>.json), or {}."""
    path = abstract_path(origin, item_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _compose_abstract(origin: str, record: dict, captured: dict) -> str:
    """The abstract cell for step 3.

    - No content (e.g. EC3, content unavailable for scraping): fall back to the title and link
      so the cell is never blank and the reviewer can still identify/locate the source.
    - scopus and hf: the real abstract, used as-is.
    - google/github (COMPOSE_ORIGINS): the LLM summary composed with its publication date and
      link, since that summary may drop those (per the review spec).
    """
    data = record.get("data", {})
    link = data.get("link") or captured.get("link") or ""
    text = captured.get("abstract") or captured.get("summary") or ""
    if not text.strip():
        title = data.get("title") or captured.get("title") or ""
        return "\n".join([f"Title: {title}", f"Link: {link}"])
    if origin not in COMPOSE_ORIGINS:
        return text
    return "\n".join([
        text,
        f"Publication date: {captured.get('publication_date', '')}",
        f"Link: {link}",
    ])


def _source_file(origin: str, item_id: str) -> str:
    """The source document name for step 4: the PDF (scopus/hf) or the Markdown (grey)."""
    if pdf_path(origin, item_id).exists():
        return f"{item_id}.pdf"
    if full_path(origin, item_id).exists():
        return f"{item_id}.md"
    return ""


def _step2_rows() -> list[list]:
    rows = []
    for origin in ORIGINS:
        records = _records(origin, 2)
        if records is None:
            print(f"[review] step 2: no output for '{origin}', skipped")
            continue
        for record in records:
            rows.append([record.get("id", ""), record.get("title", ""), ""])
    return rows


def _step3_rows() -> list[list]:
    rows = []
    for origin in ORIGINS:
        records = _records(origin, 3)
        if records is None:
            print(f"[review] step 3: no output for '{origin}', skipped")
            continue
        for record in records:
            rid = record.get("id", "")
            captured = _captured(origin, rid)
            keywords = ", ".join(captured.get("keywords", []))
            rows.append([rid, _compose_abstract(origin, record, captured), keywords, ""])
    return rows


def _step4_rows() -> list[list]:
    rows = []
    for origin in ORIGINS:
        records = _records(origin, 4)
        if records is None:
            print(f"[review] step 4: no output for '{origin}', skipped")
            continue
        for record in records:
            rid = record.get("id", "")
            title = record.get("data", {}).get("title", "")
            rows.append([rid, title, _source_file(origin, rid), ""])
    return rows


def _rq_cell(answers: dict, key: str) -> str:
    """One research-question answer as ``note`` / ``value`` / ``evidence`` lines. RQf's value is
    a list; it is joined into one line."""
    rq = answers.get(key) or {}
    value = rq.get("value", "")
    if isinstance(value, list):
        value = ", ".join(value)
    return "\n".join([
        f"note: {rq.get('note', '')}",
        f"value: {value}",
        f"evidence: {rq.get('evidence', '')}",
    ])


def _ic2_cell(criteria: dict) -> str:
    ic2 = criteria.get("IC2") or {}
    return "\n".join([
        f"type: {ic2.get('type', '')}",
        f"activity: {ic2.get('software_engineering_activity', '')}",
        f"note: {ic2.get('note', '')}",
    ])


def _ic3_cell(criteria: dict) -> str:
    ic3 = criteria.get("IC3") or {}
    return "\n".join([
        f"type: {ic3.get('type', '')}",
        f"note: {ic3.get('note', '')}",
    ])


def _step4_answers_rows() -> list[list]:
    """One row per answered step-4 item: the extracted research answers and the IC2/IC3
    classification, with an empty Agreement column (Yes/No) for the reviewer. Items with no
    answers (e.g. EC3, content unavailable) have nothing to review and are skipped."""
    rows = []
    for origin in ORIGINS:
        records = _records(origin, 4)
        if records is None:
            print(f"[review] step 4 answers: no output for '{origin}', skipped")
            continue
        for record in records:
            answers = record.get("answers")
            if not answers:
                continue
            rid = record.get("id", "")
            title = record.get("data", {}).get("title", "")
            abstract = _captured(origin, rid).get("abstract") or _captured(origin, rid).get("summary") or ""
            criteria = (record.get("screening") or {}).get("criteria") or {}
            row = [rid, title, abstract, answers.get("solution_name", "")]
            row += [_rq_cell(answers, key) for key in RQ_KEYS]
            row += [_ic2_cell(criteria), _ic3_cell(criteria), ""]
            rows.append(row)
    return rows


# Column widths per header name (Excel character units); wrapped columns hold long text.
_WIDTHS = {
    "id": 10, "ID": 10, "title": 60, "Title": 60, "abstract": 90, "Abstract": 80,
    "keywords": 40, "file": 18, "decision": 14, "Agreement": 12,
    "Solution name": 24, "IC2": 40, "IC3": 40,
}
_WRAP = {"title", "Title", "abstract", "Abstract", "keywords", "IC2", "IC3"}


def _col_width(name: str) -> int:
    return 50 if name.startswith("RQ") else _WIDTHS.get(name, 20)


def _col_wrap(name: str) -> bool:
    return name.startswith("RQ") or name in _WRAP


def _drive_folder_url() -> str:
    """The shared Google Drive folder holding the step-4 source files, from
    ``REVIEW_DRIVE_FOLDER_URL``. Empty when unset (file cells then stay plain text)."""
    config.load_dotenv()
    return os.environ.get("REVIEW_DRIVE_FOLDER_URL", "").strip()


def _write_sheet(path, header: list[str], rows: list[list], dropdown: str,
                 link_column: str | None = None, link_url: str = "") -> None:
    """Write one review workbook: a bold, frozen header, the data rows, and a list dropdown
    (``dropdown``) down the empty last column (decision / agreement).

    When ``link_column`` and ``link_url`` are given, every non-empty cell in that column
    becomes a hyperlink to ``link_url`` (the shared Drive folder), so the reviewer opens the
    folder in one click and finds the file by the name shown in the cell.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "review"

    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "A2"

    wrap = Alignment(wrap_text=True, vertical="top")
    for row in rows:
        ws.append(row)
    for col, name in enumerate(header, start=1):
        letter = get_column_letter(col)
        ws.column_dimensions[letter].width = _col_width(name)
        if _col_wrap(name):
            for cell in ws[letter][1:]:  # data rows only
                cell.alignment = wrap
        if name == link_column and link_url:
            for cell in ws[letter][1:]:
                if cell.value:  # keep empty cells (unavailable file) as-is
                    cell.hyperlink = link_url
                    cell.style = "Hyperlink"

    last_col = get_column_letter(len(header))  # the empty decision/agreement column
    validation = DataValidation(type="list", formula1=dropdown, allow_blank=True)
    ws.add_data_validation(validation)
    if rows:
        validation.add(f"{last_col}2:{last_col}{len(rows) + 1}")

    ensure_parent(path)
    wb.save(path)


def export_review_sheets() -> dict:
    """Generate the blind human-review spreadsheets for the current experiment."""
    out = review_dir()
    folder_url = _drive_folder_url()
    if not folder_url:
        print("[review] REVIEW_DRIVE_FOLDER_URL not set: step-4 file names stay plain text "
              "(set it to the shared Drive folder link to make them clickable)")
    answers_header = (["ID", "Title", "Abstract", "Solution name"] + RQ_KEYS
                      + ["IC2", "IC3", "Agreement"])
    # (name, header, rows, dropdown, link_column) — link_column is hyperlinked to folder_url.
    sheets = [
        ("step-2-review.xlsx", ["id", "title", "decision"], _step2_rows(), DECISION_VALUES, None),
        ("step-3-review.xlsx", ["id", "abstract", "keywords", "decision"], _step3_rows(),
         DECISION_VALUES, None),
        ("step-4-review.xlsx", ["id", "title", "file", "decision"], _step4_rows(),
         DECISION_VALUES, "file"),
        ("step-4-answers-review.xlsx", answers_header, _step4_answers_rows(),
         AGREEMENT_VALUES, None),
    ]
    counts = {}
    for name, header, rows, dropdown, link_column in sheets:
        path = out / name
        _write_sheet(path, header, rows, dropdown, link_column=link_column, link_url=folder_url)
        counts[name] = len(rows)
        print(f"[review] {name}: {len(rows)} rows -> {path}")
    return counts
