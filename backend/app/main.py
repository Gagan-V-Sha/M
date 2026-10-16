import asyncio
import os
import re
import secrets
import shutil
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Optional

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import pyotp
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session, joinedload

from app.core import models
from app.core.database import create_tables, get_db
import app.core.datatypes as schemas
from app.features.etd import routes as etd_routes
from app.features.importer import routes as import_routes
from app.features.importer.routes import process_standard_parse
from app.features.importer.service import (
    MinerUService,
    MINERU_AVAILABLE,
    MINERU_VERSION,
    is_mineru_ready,
)
from app.core.runtime_config import public_runtime_config
from app.security import auth

load_dotenv()

_SCAN_DISABLED_DETAIL = (
    "PDF scanning is disabled on this host. "
    "Run scans on the workstation with MINERU_ENABLED=true; "
    "mappings appear here via the shared database."
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="eTD Builder API", description="API for Electronic Technical Documentation Builder")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES = 15


@app.on_event("startup")
def startup_event():
    create_tables()


app.include_router(etd_routes.router)
app.include_router(import_routes.router)

origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _role_value(role) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _client_ip(request: Request) -> str:
    return str(request.client.host) if request.client else "unknown"


@app.post("/auth/register", response_model=schemas.UserResponse, tags=["Authentication"], summary="Register a new user")
def register(user_data: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    if not user_data.email.lower().endswith("@bec-robotics.com"):
        raise HTTPException(status_code=422, detail="Invalid email address")

    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = auth.get_password_hash(user_data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_user = models.User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        role=_role_value(user_data.role),
        is_active=True,
        gdpr_consent_at=datetime.now(timezone.utc) if user_data.gdpr_consent_accepted else None,
        gdpr_consent_ip=_client_ip(request) if user_data.gdpr_consent_accepted else None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", tags=["Authentication"], summary="Login with email/password")
@limiter.limit("5/minute")
def login(request: Request, user_credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    now = datetime.now(timezone.utc)

    if user and user.lockout_until:
        lockout_until = user.lockout_until
        if lockout_until.tzinfo is None:
            lockout_until = lockout_until.replace(tzinfo=timezone.utc)
        if lockout_until > now:
            raise HTTPException(status_code=403, detail="Account is locked. Try again later.")

    if not user or not auth.verify_password(user_credentials.password, user.hashed_password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
                user.lockout_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.mfa_enabled:
        if not user_credentials.mfa_token:
            raise HTTPException(status_code=401, detail="mfa_required")
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(user_credentials.mfa_token, valid_window=1):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

    user.failed_login_attempts = 0
    user.lockout_until = None

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    db.add(
        models.AuditLog(
            user_id=user.id,
            action="LOGIN",
            entity_type="User",
            entity_id=str(user.id),
            ip=_client_ip(request),
        )
    )
    db.commit()

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=os.getenv("FASTAPI_ENV") == "production",
        samesite="lax",
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response


@app.post("/auth/logout", tags=["Authentication"], summary="Logout user")
def logout(request: Request, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db.add(
        models.AuditLog(
            user_id=current_user.id,
            action="LOGOUT",
            entity_type="User",
            entity_id=str(current_user.id),
            ip=_client_ip(request),
        )
    )
    db.commit()
    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie(key="access_token", path="/")
    return response


@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Authentication"], summary="Get current logged in user")
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/auth/mfa/setup", response_model=schemas.MfaSetupResponse, tags=["Authentication"])
def setup_mfa(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    secret = pyotp.random_base32()
    current_user.mfa_secret = secret
    db.commit()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="eTD Builder")
    return {"secret": secret, "qr_uri": uri}


@app.post("/auth/mfa/enable", tags=["Authentication"])
def enable_mfa(
    payload: schemas.MfaVerifyRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA has not been set up")
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(payload.token, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    current_user.mfa_enabled = True
    db.commit()
    return {"message": "MFA enabled"}


@app.post("/auth/password-reset-request", tags=["Authentication"], summary="Request a password reset token")
def request_password_reset(reset_request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == reset_request.email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@app.post("/auth/password-reset-confirm", tags=["Authentication"], summary="Confirm password reset")
def confirm_password_reset(reset_request: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.reset_token == reset_request.token).first()
    expires = user.reset_token_expires if user else None
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if not user or not expires or expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    try:
        user.hashed_password = auth.get_password_hash(reset_request.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Password has been successfully reset."}


@app.post("/auth/password-change", tags=["Authentication"], summary="Change password for logged in user")
def change_password(
    password_request: schemas.PasswordChangeRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if not auth.verify_password(password_request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    try:
        current_user.hashed_password = auth.get_password_hash(password_request.new_password)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Password changed successfully"}


def natural_keys(text):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", text or "")]


@app.get("/gspr", response_model=List[schemas.GsprRequirement], tags=["Reference Data"], summary="List GSPR requirements")
def get_gspr(db: Session = Depends(get_db)):
    gsprs = db.query(models.GSPRRequirement).options(
        joinedload(models.GSPRRequirement.standard_mappings).joinedload(models.StandardGSPRMapping.standard)
    ).all()
    gsprs.sort(key=lambda x: natural_keys(x.full_reference))
    return gsprs


@app.get("/standards", response_model=List[schemas.Standard], tags=["Reference Data"], summary="List Standards")
def get_standards(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Standard)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Standard.code.ilike(search_filter)) | (models.Standard.title.ilike(search_filter))
        )
    standards = query.order_by(models.Standard.code).all()
    for standard in standards:
        latest_import = (
            db.query(models.ImportDocument)
            .filter(models.ImportDocument.standard_id == standard.id)
            .order_by(models.ImportDocument.uploaded_at.desc())
            .first()
        )
        if latest_import:
            standard.parse_status = latest_import.parse_status
            standard.parse_error = latest_import.parse_error
        else:
            standard.parse_status = "none"
            standard.parse_error = None
    return standards


@app.get("/evidence", response_model=List[schemas.EvidenceDocument], tags=["Reference Data"], summary="List Evidence Documents")
def get_evidence(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.EvidenceDocument)
    if search:
        query = query.filter(models.EvidenceDocument.title.ilike(f"%{search}%"))
    return query.order_by(models.EvidenceDocument.tdd_number).all()


@app.put("/gspr/{gspr_id}", response_model=schemas.GsprRequirement, tags=["Reference Data Update"])
def update_gspr(
    gspr_id: int,
    gspr_update: schemas.GsprUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_gspr = db.query(models.GSPRRequirement).filter(models.GSPRRequirement.id == gspr_id).first()
    if not db_gspr:
        raise HTTPException(status_code=404, detail="GSPR Requirement not found")
    update_data = gspr_update.dict(exclude_unset=True)
    standard_ids = update_data.pop("standard_ids", None)
    for key, value in update_data.items():
        setattr(db_gspr, key, value)
    if standard_ids is not None:
        db.query(models.StandardGSPRMapping).filter(
            models.StandardGSPRMapping.gspr_reference == db_gspr.full_reference
        ).delete()
        for sid in standard_ids:
            db.add(
                models.StandardGSPRMapping(
                    standard_id=sid,
                    gspr_reference=db_gspr.full_reference,
                    coverage_note="Manually linked",
                )
            )
    try:
        db.commit()
        db.refresh(db_gspr)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save changes. Please verify the data.")
    return db_gspr


@app.put("/standards/{standard_id}", response_model=schemas.Standard, tags=["Reference Data Update"])
def update_standard(
    standard_id: int,
    standard_update: schemas.StandardUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_standard = db.query(models.Standard).filter(models.Standard.id == standard_id).first()
    if not db_standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    update_data = standard_update.dict(exclude_unset=True)
    if "code" in update_data and update_data["code"] != db_standard.code:
        existing = db.query(models.Standard).filter(models.Standard.code == update_data["code"]).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Standard with code '{update_data['code']}' already exists.")
    for key, value in update_data.items():
        setattr(db_standard, key, value)
    try:
        db.commit()
        db.refresh(db_standard)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save changes. Please verify the data.")
    return db_standard


@app.put("/evidence/{evidence_id}", response_model=schemas.EvidenceDocument, tags=["Reference Data Update"])
def update_evidence(
    evidence_id: int,
    evidence_update: schemas.EvidenceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_evidence = db.query(models.EvidenceDocument).filter(models.EvidenceDocument.id == evidence_id).first()
    if not db_evidence:
        raise HTTPException(status_code=404, detail="Evidence Document not found")
    update_data = evidence_update.dict(exclude_unset=True)
    if "tdd_number" in update_data and update_data["tdd_number"] != db_evidence.tdd_number:
        existing = db.query(models.EvidenceDocument).filter(
            models.EvidenceDocument.tdd_number == update_data["tdd_number"]
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Evidence document with TDD number '{update_data['tdd_number']}' already exists.",
            )
    for key, value in update_data.items():
        setattr(db_evidence, key, value)
    try:
        db.commit()
        db.refresh(db_evidence)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save changes. Please verify the data.")
    return db_evidence


@app.post("/gspr", response_model=schemas.GsprRequirement, tags=["Reference Data Update"])
def create_gspr(
    gspr: schemas.GsprCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_admin),
):
    db_gspr = models.GSPRRequirement(**gspr.dict())
    db.add(db_gspr)
    try:
        db.commit()
        db.refresh(db_gspr)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save changes. Please verify the data.")
    return db_gspr


@app.delete("/gspr/{gspr_id}", tags=["Reference Data Update"])
def delete_gspr(
    gspr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_admin),
):
    db_gspr = db.query(models.GSPRRequirement).filter(models.GSPRRequirement.id == gspr_id).first()
    if not db_gspr:
        raise HTTPException(status_code=404, detail="GSPR Requirement not found")
    db.delete(db_gspr)
    db.commit()
    return {"message": "GSPR Requirement deleted"}


@app.post("/standards", response_model=schemas.Standard, tags=["Reference Data Update"])
def create_standard(
    standard: schemas.StandardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    existing = db.query(models.Standard).filter(models.Standard.code == standard.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Standard with code '{standard.code}' already exists.")
    db_standard = models.Standard(**standard.dict())
    db.add(db_standard)
    try:
        db.commit()
        db.refresh(db_standard)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save changes. Please verify the data.")
    return db_standard


@app.delete("/standards/{standard_id}", tags=["Reference Data Update"])
def delete_standard(
    standard_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_admin),
):
    db_standard = db.query(models.Standard).filter(models.Standard.id == standard_id).first()
    if not db_standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    db.delete(db_standard)
    db.commit()
    return {"message": "Standard deleted"}


@app.get("/config", tags=["System"], summary="Runtime role and MinerU availability")
def get_runtime_config():
    """Used by the UI to hide scan controls on Pi/runtime hosts."""
    return public_runtime_config(MINERU_AVAILABLE, MINERU_VERSION)


@app.post("/standards/{standard_id}/upload-mapping", tags=["Data Import"], summary="Upload a PDF and extract GSPR mappings")
async def upload_standard_mapping(
    standard_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    if not is_mineru_ready():
        raise HTTPException(status_code=503, detail=_SCAN_DISABLED_DETAIL)
    db_standard = db.query(models.Standard).filter(models.Standard.id == standard_id).first()
    if not db_standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    if file.content_type != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds the 50 MB upload limit")

    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    base, ext = os.path.splitext(file.filename or "upload.pdf")
    safe_base = re.sub(r"[^\w\.-]", "", base)[:25]
    safe_filename = f"{safe_base}{ext}"
    temp_path = os.path.join(upload_dir, f"temp_{safe_filename}")
    with open(temp_path, "wb") as handle:
        handle.write(contents)

    mineru_svc = MinerUService(upload_dir)
    sha256_hash = mineru_svc.calculate_sha256(temp_path)
    existing = db.query(models.ImportDocument).filter(models.ImportDocument.sha256 == sha256_hash).first()
    if existing:
        db.delete(existing)
        db.commit()

    final_dir = os.path.join(upload_dir, sha256_hash[:16])
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, safe_filename)
    shutil.move(temp_path, final_path)

    doc = models.ImportDocument(
        doc_type="STANDARD",
        original_filename=file.filename,
        stored_path=final_path,
        sha256=sha256_hash,
        uploaded_by=current_user.id,
        parse_status="pending",
        standard_id=standard_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    background_tasks.add_task(process_standard_parse, doc.id, final_path, db_standard.code, db_standard.title)
    return {"id": doc.id, "status": "pending", "message": "PDF uploaded. MinerU scan started."}


@app.get("/standards/{standard_id}/parse-status", tags=["Data Import"], summary="Check parse status for a standard's latest import")
def get_standard_parse_status(standard_id: int, db: Session = Depends(get_db)):
    doc = (
        db.query(models.ImportDocument)
        .filter(models.ImportDocument.standard_id == standard_id)
        .order_by(models.ImportDocument.uploaded_at.desc())
        .first()
    )
    if not doc:
        return {"parse_status": "none", "parse_error": None}
    return {"parse_status": doc.parse_status, "parse_error": doc.parse_error}


@app.post("/evidence", response_model=schemas.EvidenceDocument, tags=["Reference Data Update"])
def create_evidence(
    evidence: schemas.EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    existing = db.query(models.EvidenceDocument).filter(models.EvidenceDocument.tdd_number == evidence.tdd_number).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Evidence document with TDD number '{evidence.tdd_number}' already exists.")
    db_evidence = models.EvidenceDocument(**evidence.dict())
    db.add(db_evidence)
    try:
        db.commit()
        db.refresh(db_evidence)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save changes. Please verify the data.")
    return db_evidence


@app.delete("/evidence/{evidence_id}", tags=["Reference Data Update"])
def delete_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_evidence = db.query(models.EvidenceDocument).filter(models.EvidenceDocument.id == evidence_id).first()
    if not db_evidence:
        raise HTTPException(status_code=404, detail="Evidence Document not found")
    db.delete(db_evidence)
    db.commit()
    return {"message": "Evidence Document deleted"}


@app.post("/evidence/{evidence_id}/upload-pdf", tags=["Data Import"])
async def upload_evidence_pdf(
    evidence_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_evidence = db.query(models.EvidenceDocument).filter(models.EvidenceDocument.id == evidence_id).first()
    if not db_evidence:
        raise HTTPException(status_code=404, detail="Evidence Document not found")
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    base, ext = os.path.splitext(file.filename or "evidence.pdf")
    safe_base = re.sub(r"[^\w\.-]", "", base)[:25]
    file_path = os.path.join(upload_dir, f"{evidence_id}_{safe_base}{ext}")
    with open(file_path, "wb") as handle:
        handle.write(await file.read())
    db_evidence.path = file_path
    db.commit()
    return {"message": "Evidence document uploaded successfully", "path": file_path}


@app.get("/device-profiles", response_model=List[schemas.DeviceProfileResponse], tags=["Device Management"])
def get_device_profiles(db: Session = Depends(get_db)):
    return db.query(models.DeviceProfile).all()


@app.get("/device-profiles/{profile_id}", response_model=schemas.DeviceProfileResponse, tags=["Device Management"])
def get_device_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = db.query(models.DeviceProfile).filter(models.DeviceProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Device profile not found")
    return db_profile


@app.post("/device-profiles", response_model=schemas.DeviceProfileResponse, tags=["Device Management"])
def create_device_profile(
    profile: schemas.DeviceProfileCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_profile = models.DeviceProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    db.add(
        models.AuditLog(
            user_id=current_user.id,
            action="CREATE_DEVICE",
            entity_type="DeviceProfile",
            entity_id=str(db_profile.id),
            ip=_client_ip(request),
        )
    )
    db.commit()
    return db_profile


@app.put("/device-profiles/{profile_id}", response_model=schemas.DeviceProfileResponse, tags=["Device Management"])
def update_device_profile(
    profile_id: int,
    profile_update: schemas.DeviceProfileBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_profile = db.query(models.DeviceProfile).filter(models.DeviceProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Device profile not found")
    for key, value in profile_update.dict(exclude_unset=True).items():
        setattr(db_profile, key, value)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@app.delete("/device-profiles/{profile_id}", tags=["Device Management"])
def delete_device_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_or_editor),
):
    db_profile = db.query(models.DeviceProfile).filter(models.DeviceProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Device profile not found")
    db.delete(db_profile)
    db.commit()
    return {"message": "Device profile deleted successfully"}


@app.get("/device-profiles/{profile_id}/suggested-standards", response_model=List[schemas.Standard], tags=["Device Logic"])
def suggest_standards(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.DeviceProfile).filter(models.DeviceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Device profile not found")
    suggested = []
    for std in db.query(models.Standard).all():
        if not std.applicability_rules:
            suggested.append(std)
            continue
        for rule in std.applicability_rules:
            if hasattr(profile, rule.condition_key):
                profile_value = getattr(profile, rule.condition_key)
                if profile_value == (rule.condition_value.lower() == "true"):
                    suggested.append(std)
                    break
    return suggested


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/gspr/chapters", tags=["Reference Data"])
def get_gspr_chapters(db: Session = Depends(get_db)):
    chapters = db.query(models.GSPRRequirement.chapter).distinct().all()
    return sorted([c[0] for c in chapters if c[0]])


if __name__ == "__main__":
    create_tables()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio")
