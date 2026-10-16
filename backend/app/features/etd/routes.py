"""
features/etd/routes.py
=======================
eTD (Electronic Technical Documentation) editing endpoints.

Changes from audit:
  - Finding 2.1: GET /etd now requires authentication.
  - Finding 2.2: POST /etd/export/pdf now requires authentication.
  - Finding 4.4: All audit log entries now record the real client IP
    (was hardcoded to "127.0.0.1").
  - Finding 3.3: Added selectinload for many-to-many relationships
    (ETDRow.standards, ETDRow.evidence_documents) to eliminate N+1 queries.
  - Finding 1.1: IntegrityError guard on row auto-creation prevents crash
    when two concurrent requests create rows for the same device.
  - Finding 7.1: batch_update_etd now wraps all writes in try/except with
    db.rollback() on any error — atomic all-or-nothing semantics.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response, Request
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import List
import json
import os
import sys
import logging

# Playwright browser path setup
_playwright_browsers = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", ".playwright-browsers")
)
os.makedirs(_playwright_browsers, exist_ok=True)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", _playwright_browsers)
os.environ.setdefault("PLAYWRIGHT_CHROMIUM_USE_HEADLESS_SHELL", "0")

from playwright.sync_api import sync_playwright, Error as PlaywrightError
from fastapi.concurrency import run_in_threadpool
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import base64

from app.core.database import get_db
from app.security.auth import get_current_user
from app.core import models
import app.core.datatypes as schemas

logger = logging.getLogger(__name__)


def _find_bundled_chrome_exe() -> str | None:
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if not base or not os.path.isdir(base):
        return None
    if sys.platform == "win32":
        subdir, binary = "chrome-win64", "chrome.exe"
    else:
        subdir, binary = "chrome-linux", "chrome"
    for name in sorted(os.listdir(base), reverse=True):
        if name.startswith("chromium-") and "headless_shell" not in name:
            exe = os.path.join(base, name, subdir, binary)
            if os.path.isfile(exe):
                return exe
    return None


def _launch_chromium_for_pdf(playwright):
    bundled = _find_bundled_chrome_exe()
    attempts = []
    if sys.platform == "win32":
        attempts.append(("system chrome", lambda: playwright.chromium.launch(headless=True, channel="chrome")))
    if bundled:
        attempts.append(("bundled chromium", lambda: playwright.chromium.launch(headless=True, executable_path=bundled, args=["--disable-gpu"])))
    attempts.append(("playwright default", lambda: playwright.chromium.launch(headless=True)))

    last_error = None
    for label, launch in attempts:
        try:
            browser = launch()
            logger.info("PDF export using browser: %s", label)
            return browser
        except PlaywrightError as exc:
            logger.warning("PDF browser launch failed (%s): %s", label, exc)
            last_error = exc
    raise last_error


router = APIRouter(prefix="/etd", tags=["eTD Editing"])


def log_audit(db: Session, user_id: int, action: str, entity_type: str, entity_id: str, changes: dict, ip: str = "unknown"):
    """Record an audit log entry with the real client IP."""
    log = models.AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        diff_json=json.dumps(changes),
        ip=ip,  # Fix 4.4: was hardcoded to "127.0.0.1"
    )
    db.add(log)


# Fix 2.1: Added current_user dependency — was completely unauthenticated
@router.get("", response_model=List[schemas.EtdRowResponse])
def get_etd_rows(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # FIX 2.1
):
    """
    Return all ETD rows for a device.
    Auto-creates missing rows with 'not_applicable' defaults.
    Uses IntegrityError guard (Fix 1.1) to handle concurrent creation safely.
    """
    existing_gspr_ids = {
        r[0] for r in db.query(models.ETDRow.gspr_requirement_id)
        .filter(models.ETDRow.device_id == device_id).all()
    }

    all_gsprs = db.query(models.GSPRRequirement).all()
    missing_gsprs = [g for g in all_gsprs if g.id not in existing_gspr_ids]

    if missing_gsprs:
        for gspr in missing_gsprs:
            try:
                row = models.ETDRow(
                    device_id=device_id,
                    gspr_requirement_id=gspr.id,
                    applicability="not_applicable",
                    created_by="system_sync",
                )
                db.add(row)
                db.flush()  # Fix 1.1: flush individually so one conflict doesn't abort ALL rows
            except IntegrityError:
                db.rollback()  # Another worker already created this row — safe to skip
        try:
            db.commit()
        except IntegrityError:
            db.rollback()  # Full batch commit conflict — rows already exist

    # Fix 3.3: selectinload for many-to-many relationships (was N+1)
    rows = (
        db.query(models.ETDRow)
        .join(models.ETDRow.gspr_requirement)
        .filter(models.ETDRow.device_id == device_id)
        .order_by(models.GSPRRequirement.sort_order)
        .options(
            joinedload(models.ETDRow.gspr_requirement)
            .joinedload(models.GSPRRequirement.standard_mappings)
            .joinedload(models.StandardGSPRMapping.standard),
            selectinload(models.ETDRow.standards),          # Fix 3.3
            selectinload(models.ETDRow.evidence_documents), # Fix 3.3
        )
        .all()
    )
    return rows


@router.put("/{row_id}", response_model=schemas.EtdRowResponse)
def update_etd_row(
    request: Request,  # Fix 4.4
    row_id: int,
    update: schemas.EtdRowUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in [schemas.UserRole.ADMIN, schemas.UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Not authorized to edit eTD")

    row = db.query(models.ETDRow).filter(models.ETDRow.id == row_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")

    changes = {
        "old_applicability": row.applicability, "new_applicability": update.applicability,
        "old_notes": row.notes, "new_notes": update.notes,
    }
    row.applicability = update.applicability
    row.notes = update.notes
    row.updated_by = current_user.email

    log_audit(db, current_user.id, "update_row", "etd_row", str(row_id), changes,
              ip=request.client.host if request.client else "unknown")  # Fix 4.4
    db.commit()
    db.refresh(row)
    return row


@router.put("/{row_id}/standards", response_model=schemas.EtdRowResponse)
def update_row_standards(
    request: Request,  # Fix 4.4
    row_id: int,
    update: schemas.EtdRowStandardsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in [schemas.UserRole.ADMIN, schemas.UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Not authorized to edit eTD")

    row = db.query(models.ETDRow).filter(models.ETDRow.id == row_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")

    standards = db.query(models.Standard).filter(models.Standard.id.in_(update.standard_ids)).all()
    old_ids = [s.id for s in row.standards]
    log_audit(db, current_user.id, "set_standards", "etd_row", str(row_id),
              {"old": old_ids, "new": update.standard_ids},
              ip=request.client.host if request.client else "unknown")  # Fix 4.4

    row.standards = standards
    db.commit()
    db.refresh(row)
    return row


# Fix 7.1: Entire batch wrapped in try/except with explicit rollback
@router.post("/batch-update")
def batch_update_etd(
    request: Request,  # Fix 4.4
    update: schemas.EtdBatchUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in [schemas.UserRole.ADMIN, schemas.UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Not authorized to edit eTD")

    try:
        # Update device meta
        if update.device_meta:
            device = db.query(models.DeviceProfile).filter(models.DeviceProfile.id == update.device_id).first()
            if device:
                for key, value in update.device_meta.items():
                    if hasattr(device, key):
                        setattr(device, key, value)

        # Update rows
        if update.row_updates:
            row_ids = [r.id for r in update.row_updates]
            rows = db.query(models.ETDRow).filter(
                models.ETDRow.id.in_(row_ids),
                models.ETDRow.device_id == update.device_id
            ).all()
            row_map = {r.id: r for r in rows}

            for row_update in update.row_updates:
                row = row_map.get(row_update.id)
                if not row:
                    continue
                if row_update.applicability is not None:
                    row.applicability = row_update.applicability
                if row_update.notes is not None:
                    row.notes = row_update.notes
                if row_update.standard_ids is not None:
                    standards = db.query(models.Standard).filter(
                        models.Standard.id.in_(row_update.standard_ids)
                    ).all()
                    row.standards = standards
                if row_update.evidence_ids is not None:
                    evidence = db.query(models.EvidenceDocument).filter(
                        models.EvidenceDocument.id.in_(row_update.evidence_ids)
                    ).all()
                    row.evidence_documents = evidence
                row.updated_by = current_user.email

        log_audit(
            db, current_user.id, "batch_update", "etd_batch", str(update.device_id),
            {"updated_rows": len(update.row_updates), "meta_updated": bool(update.device_meta)},
            ip=request.client.host if request.client else "unknown",  # Fix 4.4
        )
        db.commit()  # Single commit — all or nothing (Fix 7.1)

    except Exception as exc:
        db.rollback()  # Fix 7.1: Explicit rollback — no partial writes
        logger.exception("batch_update failed for device_id=%s", update.device_id)
        raise HTTPException(
            status_code=500,
            detail="Update failed. No changes were saved. Please try again.",
        ) from exc

    return {"message": "Batch update successful"}


# Fix 2.2: Added current_user dependency — was completely unauthenticated
@router.post("/export/pdf")
async def export_pdf(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # FIX 2.2
):
    device = db.query(models.DeviceProfile).filter(models.DeviceProfile.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    rows = db.query(models.ETDRow).filter(models.ETDRow.device_id == device_id).all()

    import re
    def natural_keys(text):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

    rows.sort(key=lambda r: (
        r.gspr_requirement.sort_order if r.gspr_requirement else 999999,
        natural_keys(r.gspr_requirement.full_reference) if r.gspr_requirement else [],
    ))

    from itertools import groupby
    grouped_rows = []
    for chapter, items in groupby(rows, key=lambda r: r.gspr_requirement.chapter if r.gspr_requirement else "General"):
        grouped_rows.append((chapter, list(items)))

    unique_standards = {}
    unique_evidence = {}
    for row in rows:
        for std in row.standards:
            if std.id not in unique_standards:
                unique_standards[std.id] = {"code": std.code, "title": std.title or "Standard", "version": std.version or ""}
        for evid in row.evidence_documents:
            if evid.id not in unique_evidence:
                unique_evidence[evid.id] = {"tdd_number": evid.tdd_number, "title": evid.title or "Document", "version": evid.version or ""}

    templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "templates")
    env = Environment(loader=FileSystemLoader(os.path.normpath(templates_dir)))
    template = env.get_template("etd_export.html")
    html_content = template.render(
        device_name=device.name,
        model_code=device.model_code,
        document_number=device.document_number,
        purpose=device.purpose or "",
        product_description=device.product_description or "",
        export_date=datetime.now().strftime("%Y-%m-%d"),
        grouped_rows=grouped_rows,
        applicable_standards=sorted(unique_standards.values(), key=lambda x: x["code"]),
        annex_evidence=sorted(unique_evidence.values(), key=lambda x: x["tdd_number"]),
    )

    logo_base64 = ""
    try:
        etd_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.normpath(os.path.join(etd_dir, "..", "..", "..", ".."))
        logo_candidates = [
            os.path.join(project_root, "frontend", "src", "assets", "LogoBlack.png"),
            os.path.join(etd_dir, "..", "..", "assets", "LogoBlack.png"),
        ]
        for logo_path in logo_candidates:
            logo_path = os.path.normpath(logo_path)
            if os.path.isfile(logo_path):
                with open(logo_path, "rb") as image_file:
                    logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")
                break
    except OSError:
        logo_base64 = ""

    def generate_pdf_sync(html, dev_name, mod_code, doc_num, logo_b64):
        with sync_playwright() as p:
            browser = _launch_chromium_for_pdf(p)
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            header_html = f'<div style="font-size: 10px; width: 100%; padding: 0 40px; display: flex; align-items: center; justify-content: space-between;"><img src="data:image/png;base64,{logo_b64}" style="height: 20px;"><span>{dev_name} - GSPR Report</span></div>'
            footer_html = '<div style="font-size: 9px; width: 100%; padding: 0 40px; text-align: right;">Page <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
            pdf = page.pdf(
                format="A4", landscape=True, display_header_footer=True,
                header_template=header_html, footer_template=footer_html,
                margin={"top": "1.0in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"},
            )
            browser.close()
            return pdf

    try:
        pdf_bytes = await run_in_threadpool(
            generate_pdf_sync, html_content, device.name, device.model_code, device.document_number, logo_base64
        )
    except PlaywrightError as e:
        logger.exception("Playwright PDF export failed for device_id=%s", device_id)
        if "Executable doesn't exist" in str(e) or "playwright install" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="PDF export requires Playwright Chromium. Run: playwright install chromium",
            ) from e
        raise HTTPException(status_code=500, detail="PDF export failed. Please try again.") from e
    except Exception as e:
        logger.exception("PDF export failed for device_id=%s", device_id)
        raise HTTPException(status_code=500, detail="PDF export failed. Please try again.") from e

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=gspr_report_{device_id}.pdf"},
    )
