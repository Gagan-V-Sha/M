from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from enum import Enum

# Server-side sanitisation helpers (bleach + SQL metachar strip)
from app.security.validation import sanitize_text, sanitize_email, sanitize_password

# --- authentication schemas ---

class LoginRequest(BaseModel):
    """
    Login credentials.
    Server-side validation (regardless of frontend checks):
      - email: stripped, lowercased, HTML-sanitised, max 254 chars
      - password: hard length cap 128 chars (bcrypt DoS prevention)
      - mfa_token: stripped, max 10 chars (6-digit TOTP + small buffer)
    """
    email: str
    password: str
    mfa_token: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def validate_login_email(cls, v: str) -> str:
        return sanitize_email(v, max_length=254)

    @field_validator("password", mode="before")
    @classmethod
    def validate_login_password(cls, v: str) -> str:
        # Cap length only -- do NOT strip special chars from passwords
        return sanitize_password(v, max_length=128)

    @field_validator("mfa_token", mode="before")
    @classmethod
    def validate_mfa_token(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return sanitize_text(str(v), max_length=10)

class Token(BaseModel):
    # what the server sends back after successful login
    access_token: str
    token_type: str
    expires_in: int

class PasswordResetRequest(BaseModel):
    """
    Password reset request.
    email is sanitised before Pydantic's EmailStr format check runs.
    """
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def validate_reset_email(cls, v: str) -> str:
        return sanitize_email(v, max_length=254)

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class MfaSetupResponse(BaseModel):
    # info needed to scan QR code
    secret: str
    qr_uri: str

class MfaVerifyRequest(BaseModel):
    token: str

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class UserBase(BaseModel):
    """
    Shared user fields used by both UserCreate and UserResponse.
    Validators here apply to all subclasses (register, admin create-user, etc.).
    """
    email: EmailStr
    name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    is_active: bool = True

    @field_validator("email", mode="before")
    @classmethod
    def validate_user_email(cls, v: str) -> str:
        # Sanitise before Pydantic's EmailStr validation runs
        return sanitize_email(v, max_length=254)

    @field_validator("name", mode="before")
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Display name / full name:
          - Strip HTML tags and SQL meta-characters
          - Max 100 characters
          - Angle brackets < > not allowed (XSS prevention)
        """
        if v is None:
            return v
        cleaned = sanitize_text(str(v), max_length=100)
        # Extra guard: reject any remaining angle brackets after bleach
        if "<" in cleaned or ">" in cleaned:
            raise ValueError("Display name contains disallowed characters")
        return cleaned


class UserCreate(UserBase):
    """
    Registration payload.
    password is length-capped server-side; strength rules are enforced
    inside auth.get_password_hash().
    gdpr_consent_accepted must be True for registration to succeed.
    """
    password: str
    gdpr_consent_accepted: bool = False  # Fix 8.2 — GDPR explicit consent

    @field_validator("password", mode="before")
    @classmethod
    def validate_register_password(cls, v: str) -> str:
        # Hard length cap; do NOT strip special chars from passwords
        return sanitize_password(v, max_length=128)

    @field_validator("gdpr_consent_accepted", mode="before")
    @classmethod
    def validate_gdpr_consent(cls, v) -> bool:
        if not v:
            raise ValueError("You must accept the Privacy Policy to register.")
        return bool(v)

class UserResponse(UserBase):
    # what we show when listing users
    id: int
    created_at: datetime
    mfa_enabled: bool
    gdpr_consent_at: Optional[datetime] = None  # Fix 8.2
    
    model_config = ConfigDict(from_attributes=True)

# --- regulatory and technical data schemas ---

class StandardBase(BaseModel):
    code: str
    title: Optional[str] = None
    version: Optional[str] = None
    harmonised: bool = False
    status: Optional[str] = None

class Standard(StandardBase):
    id: int
    publication_date: Optional[datetime] = None
    # MinerU scan progress: none | processing | completed | failed
    parse_status: Optional[str] = None
    parse_error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class GsprRequirementBase(BaseModel):
    chapter: Optional[str] = None
    section: Optional[str] = None
    full_reference: str
    text: Optional[str] = None
    parent_id: Optional[int] = None

class StandardGSPRMappingResponse(BaseModel):
    # links a standard to a GSPR section
    # standard_id can be None for legacy rows where the standard was deleted
    id: int
    standard_id: Optional[int] = None
    gspr_reference: str
    iso_clause: Optional[str] = None
    coverage_note: Optional[str] = None
    standard: Optional[Standard] = None

    model_config = ConfigDict(from_attributes=True)

class GsprRequirement(GsprRequirementBase):
    id: int
    standard_mappings: List[StandardGSPRMappingResponse] = []

    model_config = ConfigDict(from_attributes=True)

class EvidenceDocumentBase(BaseModel):
    tdd_number: str
    title: Optional[str] = None
    version: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None

class EvidenceDocument(EvidenceDocumentBase):
    id: int
    owner: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- device profile schemas ---

class DeviceProfileBase(BaseModel):
    name: str
    sterile: bool = False
    body_contact: bool = False
    implantable: bool = False
    electrical: bool = False
    software: bool = False
    model_code: Optional[str] = None
    document_number: Optional[str] = None
    purpose: Optional[str] = None
    product_description: Optional[str] = None

class DeviceProfile(DeviceProfileBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- eTD (Technical Documentation) schemas ---

class EtdRowUpdate(BaseModel):
    applicability: str
    notes: Optional[str] = None

    @field_validator("notes", mode="before")
    @classmethod
    def cap_notes_length(cls, v: Optional[str]) -> Optional[str]:
        """Fix 2.4: Prevent massive payloads from crashing Playwright PDF renderer."""
        if v and len(v) > 5000:
            raise ValueError("Notes exceed maximum length of 5000 characters")
        return v

class EtdRowStandardsUpdate(BaseModel):
    standard_ids: List[int]

class EtdRowEvidenceUpdate(BaseModel):
    evidence_ids: List[int]

class EtdRowResponse(BaseModel):
    # represents one row in the final technical documentation table
    id: int
    device_id: int
    gspr_requirement_id: int
    applicability: Optional[str] = None
    notes: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    gspr_requirement: Optional[GsprRequirement] = None
    standards: List[Standard] = []
    evidence_documents: List[EvidenceDocument] = []

    model_config = ConfigDict(from_attributes=True)

class RowBatchUpdate(BaseModel):
    id: int
    applicability: Optional[str] = None
    notes: Optional[str] = None
    standard_ids: Optional[List[int]] = None
    evidence_ids: Optional[List[int]] = None

class EtdBatchUpdateRequest(BaseModel):
    device_id: int
    device_meta: Optional[dict] = None
    row_updates: List[RowBatchUpdate] = []

# --- update and create schemas ---

class StandardUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    version: Optional[str] = None
    harmonised: Optional[bool] = None
    status: Optional[str] = None

class GsprUpdate(BaseModel):
    chapter: Optional[str] = None
    section: Optional[str] = None
    full_reference: Optional[str] = None
    text: Optional[str] = None
    parent_id: Optional[int] = None
    standard_ids: Optional[List[int]] = None

class EvidenceUpdate(BaseModel):
    tdd_number: Optional[str] = None
    title: Optional[str] = None
    version: Optional[str] = None
    type: Optional[str] = None
    owner: Optional[str] = None
    path: Optional[str] = None

class StandardCreate(StandardBase):
    pass

class GsprCreate(GsprRequirementBase):
    pass

class EvidenceCreate(EvidenceDocumentBase):
    owner: Optional[str] = None

class DeviceProfileCreate(DeviceProfileBase):
    pass

class DeviceProfileResponse(DeviceProfileBase):
    id: int
    # OPTION A: exposes which user owns this device
    # Useful for the frontend to conditionally show Delete only to the owner
    owner_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
