import os
import json
import shutil
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.security.auth import get_current_user
from app.core import models
import app.core.datatypes as schemas
from app.features.importer.service import (
    MinerUService,
    MINERU_VERSION,
    is_mineru_ready,
)
from app.features.importer.standard_parser import (
    inspect_middle_json,
    parse_standard_and_save_mappings,
)

logger = logging.getLogger(__name__)

# this router handles all the PDF and data imports
router = APIRouter(prefix="/imports", tags=["Imports"])

# directory where uploaded files are stored
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# service for AI-based PDF parsing (sha256 / uploads also used when MinerU is off)
mineru_service = MinerUService(UPLOAD_DIR)

_SCAN_DISABLED_DETAIL = (
    "PDF scanning is disabled on this host. "
    "Run scans on the workstation with MINERU_ENABLED=true; "
    "mappings appear here via the shared database."
)


def require_mineru_ready() -> None:
    if not is_mineru_ready():
        raise HTTPException(status_code=503, detail=_SCAN_DISABLED_DETAIL)

# helper to make filenames safe for the filesystem
def clean_name(filename: str) -> str:
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

# helper to make sure the file is actually a PDF
def validate_pdf(file: UploadFile):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

# Fix 3.5: 50 MB upload limit to prevent disk-filling DoS
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

# helper to save the uploaded file to disk with size cap
def save_upload_file(upload_file: UploadFile, destination: str):
    total = 0
    with open(destination, "wb") as buffer:
        for chunk in iter(lambda: upload_file.file.read(65536), b""):
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                buffer.close()
                if os.path.exists(destination):
                    os.remove(destination)
                raise HTTPException(
                    status_code=413,
                    detail="File exceeds the 50 MB upload limit."
                )
            buffer.write(chunk)

@router.post("/mdr")
def import_mdr(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    require_mineru_ready()
    # import a Medical Device Regulation (MDR) report
    validate_pdf(file)
    
    safe_filename = clean_name(file.filename)
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{safe_filename}")
    save_upload_file(file, temp_path)
    sha256_hash = mineru_service.calculate_sha256(temp_path)
    
    # check if we already have this exact file
    existing = db.query(models.ImportDocument).filter(models.ImportDocument.sha256 == sha256_hash).first()
    if existing and existing.parse_status != "failed":
        os.remove(temp_path)
        raise HTTPException(status_code=409, detail="This file has already been uploaded.")
        
    # move file to a unique folder based on its hash
    final_dir = os.path.join(UPLOAD_DIR, sha256_hash[:16])
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, safe_filename)
    shutil.move(temp_path, final_path)
    
    # record the import in the database (reuse the failed record on retry,
    # since sha256 is unique and inserting again would crash)
    if existing:
        doc = existing
        doc.doc_type = "MDR"
        doc.original_filename = file.filename
        doc.stored_path = final_path
        doc.uploaded_by = current_user.id
        doc.parse_status = "pending"
        doc.parse_error = None
    else:
        doc = models.ImportDocument(
            doc_type="MDR",
            original_filename=file.filename,
            stored_path=final_path,
            sha256=sha256_hash,
            uploaded_by=current_user.id,
            parse_status="pending"
        )
        db.add(doc)
    db.commit()
    
    # start the AI parsing in the background so the user doesn't have to wait
    background_tasks.add_task(process_mdr_parse, doc.id, final_path)
    return {"id": doc.id, "status": "pending"}

@router.post("/standard")
def import_standard(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    code: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    require_mineru_ready()
    # import a technical standard (like an ISO document)
    validate_pdf(file)
    
    safe_filename = clean_name(file.filename)
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{safe_filename}")
    save_upload_file(file, temp_path)
    sha256_hash = mineru_service.calculate_sha256(temp_path)
    
    # duplicate check
    existing = db.query(models.ImportDocument).filter(models.ImportDocument.sha256 == sha256_hash).first()
    if existing and existing.parse_status != "failed":
        os.remove(temp_path)
        raise HTTPException(status_code=409, detail="Standard already uploaded.")

    final_dir = os.path.join(UPLOAD_DIR, sha256_hash[:16])
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, safe_filename)
    shutil.move(temp_path, final_path)
    
    # reuse the failed record on retry (sha256 is unique)
    if existing:
        doc = existing
        doc.doc_type = "STANDARD"
        doc.original_filename = file.filename
        doc.stored_path = final_path
        doc.uploaded_by = current_user.id
        doc.parse_status = "pending"
        doc.parse_error = None
    else:
        doc = models.ImportDocument(
            doc_type="STANDARD",
            original_filename=file.filename,
            stored_path=final_path,
            sha256=sha256_hash,
            uploaded_by=current_user.id,
            parse_status="pending"
        )
        db.add(doc)
    db.commit()
    
    # trigger background parsing for standards
    background_tasks.add_task(process_standard_parse, doc.id, final_path, code, title)
    return {"id": doc.id, "status": "pending"}

@router.post("/evidence")
def import_evidence_doc(
    file: UploadFile = File(...),
    tdd_number: str = Form(...),
    title: str = Form(...),
    version: str = Form("1.0"),
    type: str = Form("Test Report"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # import evidence documents (like test reports)
    validate_pdf(file)
    
    # make sure we don't already have this TDD number
    if db.query(models.EvidenceDocument).filter(models.EvidenceDocument.tdd_number == tdd_number).first():
        raise HTTPException(status_code=400, detail=f"Evidence with TDD {tdd_number} already exists")

    safe_filename = clean_name(file.filename)
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{safe_filename}")
    save_upload_file(file, temp_path)
    sha256_hash = mineru_service.calculate_sha256(temp_path)
    
    # check for duplicate file content
    existing = db.query(models.ImportDocument).filter(models.ImportDocument.sha256 == sha256_hash).first()
    if existing and existing.parse_status != "failed":
        os.remove(temp_path)
        raise HTTPException(status_code=409, detail="This exact file has already been uploaded.")
        
    final_dir = os.path.join(UPLOAD_DIR, sha256_hash[:16])
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, safe_filename)
    shutil.move(temp_path, final_path)
    
    # record it as an import so we can detect duplicates later
    # (reuse the failed record on retry since sha256 is unique)
    if existing:
        import_doc = existing
        import_doc.doc_type = "EVIDENCE"
        import_doc.original_filename = file.filename
        import_doc.stored_path = final_path
        import_doc.uploaded_by = current_user.id
        import_doc.parse_status = "completed"
        import_doc.parse_error = None
    else:
        import_doc = models.ImportDocument(
            doc_type="EVIDENCE",
            original_filename=file.filename,
            stored_path=final_path,
            sha256=sha256_hash,
            uploaded_by=current_user.id,
            parse_status="completed" # evidence doesn't need AI parsing for now
        )
        db.add(import_doc)

    # create the actual evidence record
    evidence = models.EvidenceDocument(
        tdd_number=tdd_number,
        title=title,
        version=version,
        type=type,
        owner=current_user.name,
        path=final_path
    )
    db.add(evidence)
    db.commit()
    
    return {"status": "completed", "evidence_id": evidence.id}

def _load_middle_json(path: Optional[str]) -> Optional[Dict]:
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        logger.warning("Could not read middle JSON at %s: %s", path, exc)
        return None


@router.get("/scan-review")
def list_scan_review(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Temporary QA list: every standard plus latest MinerU scan status."""
    standards = db.query(models.Standard).order_by(models.Standard.code).all()
    rows = []
    for standard in standards:
        latest = (
            db.query(models.ImportDocument)
            .filter(models.ImportDocument.standard_id == standard.id)
            .order_by(models.ImportDocument.uploaded_at.desc())
            .first()
        )
        mapping_count = (
            db.query(models.StandardGSPRMapping)
            .filter(models.StandardGSPRMapping.standard_id == standard.id)
            .count()
        )
        status = (latest.parse_status if latest else None) or standard.parse_status or "none"
        rows.append(
            {
                "standard_id": standard.id,
                "code": standard.code,
                "title": standard.title,
                "parse_status": status,
                "parse_error": (latest.parse_error if latest else None) or standard.parse_error,
                "filename": latest.original_filename if latest else None,
                "uploaded_at": latest.uploaded_at.isoformat() if latest and latest.uploaded_at else None,
                "import_id": latest.id if latest else None,
                "mapping_count": mapping_count,
                "has_middle_json": bool(
                    (latest and latest.parsed_json_path and os.path.exists(latest.parsed_json_path))
                    or (standard.mapping_json_path and os.path.exists(standard.mapping_json_path))
                ),
            }
        )
    return rows


@router.get("/scan-review/{standard_id}")
def get_scan_review(
    standard_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Temporary QA detail: scan status plus extracted clauses and Annex Z mappings."""
    standard = db.query(models.Standard).filter(models.Standard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")

    latest = (
        db.query(models.ImportDocument)
        .filter(models.ImportDocument.standard_id == standard.id)
        .order_by(models.ImportDocument.uploaded_at.desc())
        .first()
    )
    saved_mappings = (
        db.query(models.StandardGSPRMapping)
        .filter(models.StandardGSPRMapping.standard_id == standard.id)
        .all()
    )
    json_path = None
    if latest and latest.parsed_json_path:
        json_path = latest.parsed_json_path
    elif standard.mapping_json_path:
        json_path = standard.mapping_json_path

    middle = _load_middle_json(json_path)
    inspection = inspect_middle_json(middle) if middle else None
    status = (latest.parse_status if latest else None) or standard.parse_status or "none"

    return {
        "standard_id": standard.id,
        "code": standard.code,
        "title": standard.title,
        "parse_status": status,
        "parse_error": (latest.parse_error if latest else None) or standard.parse_error,
        "filename": latest.original_filename if latest else None,
        "uploaded_at": latest.uploaded_at.isoformat() if latest and latest.uploaded_at else None,
        "import_id": latest.id if latest else None,
        "middle_json_path": json_path,
        "middle_json_loaded": bool(middle),
        "inspection": inspection,
        "saved_mappings": [
            {
                "id": row.id,
                "iso_clause": row.iso_clause,
                "gspr_reference": row.gspr_reference,
                "coverage_note": row.coverage_note,
            }
            for row in saved_mappings
        ],
        "engine_note": {
            "recommended": "MinerU",
            "version": MINERU_VERSION,
            "reason": (
                f"Using MinerU {MINERU_VERSION} (pipeline + PP-OCRv6). Annex Z mapping "
                "needs typed layout (titles, table HTML, reading order) in middle JSON. "
                "Baidu Unlimited-OCR is strong at long-page text but weaker as a "
                "table/layout tree, and the cloud API would send ISO PDFs off-box."
            ),
        },
    }


@router.get("")
def list_imports(
    doc_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # Fix 2.3: was unauthenticated
):
    # list all recent document imports
    query = db.query(models.ImportDocument)
    if doc_type:
        query = query.filter(models.ImportDocument.doc_type == doc_type.upper())
    return query.order_by(models.ImportDocument.uploaded_at.desc()).all()

# --- background processing functions ---

# Fix 6.3: Hard 10-minute timeout on background parse tasks
PARSE_TIMEOUT_SECONDS = 600

def process_mdr_parse(import_id: int, file_path: str):
    """Background task: parse an uploaded MDR report PDF with MinerU."""
    db = next(get_db())
    doc = db.query(models.ImportDocument).filter(models.ImportDocument.id == import_id).first()
    if not doc:
        return
    try:
        doc.parse_status = "processing"
        db.commit()

        import threading
        result: dict = {}

        def _run():
            result["out"] = mineru_service.parse_pdf(file_path, output_dir=os.path.join(UPLOAD_DIR, "output"))

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=PARSE_TIMEOUT_SECONDS)

        if t.is_alive():
            # Task is still running past timeout — mark as failed
            doc.parse_status = "failed"
            doc.parse_error = "Parse timed out after 10 minutes"
            db.commit()
            logger.error("MDR parse timed out for import_id=%s", import_id)
            return

        parse_result = result.get("out", {"success": False, "error": "Unknown error"})
        if parse_result["success"]:
            doc.parse_status = "completed"
            doc.parsed_json_path = parse_result.get("json_path")
        else:
            doc.parse_status = "failed"
            doc.parse_error = str(parse_result.get("error", "Unknown MinerU error"))[:500]
        db.commit()
    except Exception as e:
        logger.exception("MDR parse failed for import_id=%s", import_id)
        if doc:
            doc.parse_status = "failed"
            doc.parse_error = str(e)[:500]  # Cap error string to avoid DB bloat
            db.commit()
    finally:
        db.close()


def process_standard_parse(import_id: int, file_path: str, code: str, title: str):
    """Background task: parse an ISO standard PDF and extract Annex Z → GSPR mappings."""
    db = next(get_db())
    doc = db.query(models.ImportDocument).filter(models.ImportDocument.id == import_id).first()
    if not doc:
        return
    try:
        doc.parse_status = "processing"
        db.commit()

        import threading
        result: dict = {}

        def _run():
            output_dir = os.path.join(UPLOAD_DIR, "output")
            result["out"] = mineru_service.parse_pdf(file_path, output_dir=output_dir)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=PARSE_TIMEOUT_SECONDS)

        if t.is_alive():
            doc.parse_status = "failed"
            doc.parse_error = "Parse timed out after 10 minutes"
            if doc.standard_id:
                standard = db.query(models.Standard).filter(models.Standard.id == doc.standard_id).first()
                if standard:
                    standard.parse_status = "failed"
                    standard.parse_error = doc.parse_error
            db.commit()
            logger.error("Standard parse timed out for import_id=%s", import_id)
            return

        parse_result = result.get("out", {"success": False, "error": "Unknown error"})

        if parse_result["success"]:
            doc.parsed_json_path = parse_result.get("json_path")

            # If this import is linked to a Standard record, save GSPR mappings
            if doc.standard_id:
                standard = db.query(models.Standard).filter(models.Standard.id == doc.standard_id).first()
                if standard:
                    summary = parse_standard_and_save_mappings(
                        standard_id=doc.standard_id,
                        middle_json=parse_result["middle_json"],
                        db=db,
                    )
                    standard.mapping_json_path = parse_result.get("json_path")
                    standard.parse_status = "completed"
                    logger.info(
                        "Standard %s (%s): %d clauses found, %d mappings saved",
                        code, doc.standard_id, summary["clauses_found"], summary["mappings_saved"]
                    )

            doc.parse_status = "completed"
            db.commit()
        else:
            doc.parse_status = "failed"
            doc.parse_error = str(parse_result.get("error", "Unknown MinerU error"))[:500]
            if doc.standard_id:
                standard = db.query(models.Standard).filter(models.Standard.id == doc.standard_id).first()
                if standard:
                    standard.parse_status = "failed"
                    standard.parse_error = doc.parse_error
            db.commit()
    except Exception as e:
        logger.exception("Standard parse failed for import_id=%s", import_id)
        if doc:
            doc.parse_status = "failed"
            doc.parse_error = str(e)[:500]
            db.commit()
    finally:
        db.close()
