"""
standard_parser.py — MinerU-based ISO standard PDF parser for GSPR mapping.

After MinerU converts a standard PDF into a structured 'middle JSON', this module
walks through the content blocks and extracts:
  1. ISO clause references (e.g. "4.1", "8.5.3")
  2. The clause title / text
  3. Any Annex Z table rows linking the ISO clause to a GSPR requirement reference
     (e.g. "Chapter I, Section 1 → clause 4.2")

The results are stored as StandardGSPRMapping rows in the database.
"""

import html
import re
import json
import logging
import os
import shutil
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ─── Regex patterns ──────────────────────────────────────────────────────────
# Matches ISO clause numbers like "4.1", "8.5.3", "A.1"
CLAUSE_RE = re.compile(r'^([A-Z]?\d+(?:\.\d+)*)\s+(.+)')

# Matches GSPR/MDR requirement references like "Annex I, Section 1" or "10.1" or "Chapter II"
GSPR_REF_RE = re.compile(
    r'(?:Annex\s+I[,\s]+)?'
    r'(?:(?:Chapter|Section|Clause|Part)\s+[IVX\d]+[,\s]*(?:Section\s+\d+)?|'
    r'\d+(?:\.\d+)*)',
    re.IGNORECASE
)

_TR_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_TD_RE = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(fragment: str) -> str:
    text = _TAG_RE.sub(" ", fragment or "")
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def html_table_rows(html_src: str) -> List[str]:
    """Flatten a MinerU <table> HTML fragment into pipe-separated row strings."""
    rows = []
    for tr in _TR_RE.findall(html_src or ""):
        cells = [_strip_html(c) for c in _TD_RE.findall(tr)]
        if any(cells):
            rows.append(" | ".join(cells))
    return rows


def _append_line_text(block_type: str, block: Dict[str, Any], out: List[Dict[str, str]]) -> None:
    for line in block.get("lines", []) or []:
        parts = []
        for span in line.get("spans", []) or []:
            html_src = span.get("html")
            if html_src:
                for row in html_table_rows(html_src):
                    out.append({"type": "table_row", "text": row})
            content = (span.get("content") or "").strip()
            if content:
                parts.append(content)
        text = " ".join(parts).strip()
        if text and block_type in ("text", "title", "interline_equation"):
            out.append({"type": block_type, "text": text})


def _flatten_table_cells(block: Dict[str, Any], out: List[Dict[str, str]]) -> None:
    for row in block.get("cells", []) or []:
        if isinstance(row, list):
            row_text = " | ".join(
                (cell.get("content", "") if isinstance(cell, dict) else str(cell)).strip()
                for cell in row
            )
        elif isinstance(row, dict):
            row_text = (row.get("content") or "").strip()
        else:
            row_text = str(row)
        if row_text.strip():
            out.append({"type": "table_row", "text": row_text})


def _walk_layout_blocks(layout_blocks: List[Dict[str, Any]], out: List[Dict[str, str]]) -> None:
    for block in layout_blocks or []:
        block_type = block.get("type", "")
        _append_line_text(block_type, block, out)
        if block_type == "table":
            _flatten_table_cells(block, out)
        nested = block.get("blocks")
        if nested:
            _walk_layout_blocks(nested, out)


def extract_text_blocks(middle_json: Dict[str, Any]) -> List[Dict[str, str]]:
    """Walk the MinerU middle JSON and return a flat list of text blocks with their type."""
    blocks: List[Dict[str, str]] = []
    pdf_info = middle_json.get("pdf_info", [])
    for page in pdf_info:
        page_blocks = page.get("preproc_blocks") or page.get("para_blocks") or []
        _walk_layout_blocks(page_blocks, blocks)
    return blocks


def inspect_middle_json(middle_json: Dict[str, Any]) -> Dict[str, Any]:
    """QA snapshot: layout stats plus clauses and Annex Z mappings we actually extract."""
    pdf_info = middle_json.get("pdf_info") or []
    layout_types: Counter = Counter()
    html_tables = 0
    table_blocks = 0

    def _count(layout_blocks):
        nonlocal html_tables, table_blocks
        for block in layout_blocks or []:
            btype = block.get("type") or "unknown"
            layout_types[btype] += 1
            if btype == "table":
                table_blocks += 1
            for line in block.get("lines", []) or []:
                for span in line.get("spans", []) or []:
                    if span.get("html"):
                        html_tables += 1
            _count(block.get("blocks"))

    for page in pdf_info:
        _count(page.get("preproc_blocks") or page.get("para_blocks") or [])

    extracted = extract_text_blocks(middle_json)
    clauses = extract_clauses(extracted)
    mappings = extract_annex_z_mappings(extracted)
    extracted_counts = Counter(b["type"] for b in extracted)
    table_rows = [b["text"] for b in extracted if b["type"] == "table_row"]
    annex_hits = [b["text"] for b in extracted if re.search(r"Annex\s+Z", b["text"], re.I)]
    warnings = []
    if table_blocks and not table_rows:
        warnings.append("MinerU detected table blocks but no rows were flattened.")
    if html_tables == 0 and table_blocks:
        warnings.append("Table blocks have no HTML cells — layout OCR may have missed table content.")
    if not mappings:
        warnings.append("No Annex Z → GSPR mappings extracted. This is the mapping we need for eTD.")

    return {
        "page_count": len(pdf_info),
        "layout_block_counts": dict(layout_types),
        "extracted_block_counts": dict(extracted_counts),
        "table_blocks_detected": table_blocks,
        "html_tables_detected": html_tables,
        "table_row_count": len(table_rows),
        "table_row_samples": table_rows[:40],
        "clause_count": len(clauses),
        "clauses": [
            {
                "clause_ref": c["clause_ref"],
                "title": c["title"],
                "body_preview": (c.get("body") or "").strip()[:240],
            }
            for c in clauses[:200]
        ],
        "annex_z_mentions": [t[:300] for t in annex_hits[:20]],
        "mapping_count": len(mappings),
        "annex_z_mappings": mappings[:200],
        "title_samples": [b["text"][:220] for b in extracted if b["type"] == "title"][:30],
        "warnings": warnings,
    }


def extract_clauses(blocks: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Scan text blocks for ISO clause headings and collect their body text.
    Returns a list of dicts: {clause_ref, title, body}
    """
    clauses = []
    current_clause = None

    for block in blocks:
        text = block["text"]
        match = CLAUSE_RE.match(text) if block["type"] in ("title", "text") else None
        if match:
            if current_clause:
                clauses.append(current_clause)
            current_clause = {
                "clause_ref": match.group(1),
                "title": match.group(2).strip(),
                "body": "",
            }
        elif current_clause:
            current_clause["body"] += " " + text

    if current_clause:
        clauses.append(current_clause)

    return clauses


def extract_annex_z_mappings(blocks: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Look for Annex Z / ZA / ZB table rows that map ISO clauses to GSPR/MDR requirements.
    Returns list of {iso_clause, gspr_reference, coverage_note}.
    """
    mappings = []
    in_annex_z = False

    for block in blocks:
        text = block["text"]
        # Detect entering an Annex Z section
        if re.search(r'Annex\s+Z[A-Z]?\b', text, re.IGNORECASE):
            in_annex_z = True

        if not in_annex_z:
            continue

        if block["type"] == "table_row":
            parts = [p.strip() for p in text.split("|")]
            if len(parts) >= 2:
                # First column typically has the ISO clause ref
                iso_col = parts[0]
                # Remaining columns may contain the GSPR reference
                rest = " ".join(parts[1:])
                iso_match = re.match(r'^([A-Z]?\d+(?:\.\d+)*)', iso_col)
                gspr_matches = GSPR_REF_RE.findall(rest)
                if iso_match and gspr_matches:
                    for gspr_ref in gspr_matches:
                        mappings.append({
                            "iso_clause": iso_match.group(1),
                            "gspr_reference": gspr_ref.strip(),
                            "coverage_note": rest,
                        })

    return mappings


def parse_standard_and_save_mappings(
    standard_id: int,
    middle_json: Dict[str, Any],
    db,
) -> Dict[str, Any]:
    """
    Given a MinerU middle_json for a standard PDF:
      1. Extract clauses
      2. Extract Annex Z → GSPR mappings
      3. Save StandardGSPRMapping rows to the DB (upsert by iso_clause)
    Returns a summary dict.
    """
    from app.core.models import StandardGSPRMapping

    blocks = extract_text_blocks(middle_json)
    clauses = extract_clauses(blocks)
    annex_mappings = extract_annex_z_mappings(blocks)

    logger.info(
        "Standard %d: found %d clauses, %d Annex-Z mappings",
        standard_id, len(clauses), len(annex_mappings)
    )

    saved = 0
    for m in annex_mappings:
        # Avoid duplicates — check for existing row with same standard + iso_clause
        existing = (
            db.query(StandardGSPRMapping)
            .filter_by(standard_id=standard_id, iso_clause=m["iso_clause"])
            .first()
        )
        if existing:
            existing.gspr_reference = m["gspr_reference"]
            existing.coverage_note = m["coverage_note"]
        else:
            row = StandardGSPRMapping(
                standard_id=standard_id,
                iso_clause=m["iso_clause"],
                gspr_reference=m["gspr_reference"],
                coverage_note=m["coverage_note"],
            )
            db.add(row)
        saved += 1

    db.commit()

    return {
        "clauses_found": len(clauses),
        "mappings_saved": saved,
    }
