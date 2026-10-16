from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# these tables help link rows together (many-to-many)
# for example, one GSPR row can have multiple ISO standards
etd_row_standards = Table(
    'etd_row_standards', Base.metadata,
    Column('etd_row_id', Integer, ForeignKey('etd_rows.id'), primary_key=True),
    Column('standard_id', Integer, ForeignKey('standards.id'), primary_key=True)
)

etd_row_evidence = Table(
    'etd_row_evidence', Base.metadata,
    Column('etd_row_id', Integer, ForeignKey('etd_rows.id'), primary_key=True),
    Column('evidence_id', Integer, ForeignKey('evidence_documents.id'), primary_key=True)
)

# represents a technical standard like ISO 13485
class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # like 'ISO 13485'
    title = Column(String)
    version = Column(String)
    harmonised = Column(Boolean, default=False)
    oj_reference = Column(String)
    status = Column(String)
    publication_date = Column(DateTime)

    # PDF processing fields (populated after upload-mapping)
    pdf_path = Column(String, nullable=True)           # path to uploaded PDF on disk
    mapping_json_path = Column(String, nullable=True)  # path to MinerU middle JSON output
    parse_status = Column(String, default="none")      # none | processing | completed | failed
    parse_error = Column(Text, nullable=True)          # error message if parsing failed

    # relationships to other tables
    applicability_rules = relationship("StandardApplicabilityRule", back_populates="standard")
    gspr_mappings = relationship("StandardGSPRMapping", back_populates="standard")
    etd_rows = relationship("ETDRow", secondary=etd_row_standards, back_populates="standards")


# these are the actual GSPR regulatory requirements from the EU
class GSPRRequirement(Base):
    __tablename__ = "gspr_requirements"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("gspr_requirements.id"), nullable=True)
    chapter = Column(String) # like 'Chapter I'
    section = Column(String) # like 'Section 1'
    full_reference = Column(String, index=True) # like '10.1'
    text = Column(Text)
    sort_order = Column(Integer, default=0)

    # allows requirements to have sub-requirements
    children = relationship("GSPRRequirement", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("GSPRRequirement", back_populates="children", remote_side=[id])
    
    standard_mappings = relationship("StandardGSPRMapping", back_populates="gspr")
    etd_rows = relationship("ETDRow", back_populates="gspr_requirement")


# maps which standards help fulfill which GSPR requirement
class StandardGSPRMapping(Base):
    __tablename__ = "standard_gspr_mapping"

    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"))
    gspr_reference = Column(String, ForeignKey("gspr_requirements.full_reference"))
    iso_clause = Column(String)
    coverage_note = Column(Text)

    standard = relationship("Standard", back_populates="gspr_mappings")
    gspr = relationship("GSPRRequirement", back_populates="standard_mappings")


# info about a specific medical device we are building documentation for
class DeviceProfile(Base):
    __tablename__ = "device_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # flags to describe device features
    sterile = Column(Boolean, default=False)
    body_contact = Column(Boolean, default=False)
    implantable = Column(Boolean, default=False)
    electrical = Column(Boolean, default=False)
    software = Column(Boolean, default=False)
    model_code = Column(String)
    document_number = Column(String)
    purpose = Column(Text)
    product_description = Column(Text)

    # OPTION A: per-user isolation — tracks which user created this device
    # nullable=True so existing devices in the DB are not broken by the migration
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User", foreign_keys=[owner_id])

    etd_rows = relationship("ETDRow", back_populates="device", cascade="all, delete-orphan")


# rules to automatically suggest standards based on device features
class StandardApplicabilityRule(Base):
    __tablename__ = "standard_applicability_rules"

    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"))
    condition_key = Column(String) # like 'sterile'
    condition_value = Column(String) # like 'True'

    standard = relationship("Standard", back_populates="applicability_rules")


# info about a test report or other piece of evidence
class EvidenceDocument(Base):
    __tablename__ = "evidence_documents"

    id = Column(Integer, primary_key=True, index=True)
    tdd_number = Column(String, unique=True, index=True)
    title = Column(String)
    version = Column(String)
    type = Column(String)
    owner = Column(String)
    path = Column(String) # path to the file on the server

    etd_rows = relationship("ETDRow", secondary=etd_row_evidence, back_populates="evidence_documents")


# users of the system
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="viewer")  # admin, editor, or viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    reset_token = Column(String, index=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    mfa_secret = Column(String, nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)
    # Fix 8.2 — GDPR consent tracking
    gdpr_consent_at = Column(DateTime, nullable=True)   # timestamp of explicit consent
    gdpr_consent_ip = Column(String, nullable=True)     # IP address at consent time

    audit_logs = relationship("AuditLog", back_populates="user")


# records every important action for security auditing
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)     # like 'LOGIN' or 'DELETE'
    entity_type = Column(String)
    entity_id = Column(String)
    diff_json = Column(Text)    # what exactly changed
    timestamp = Column(DateTime, server_default=func.now(), index=True)  # Fix 8.3: indexed for 90-day purge
    ip = Column(String)

    user = relationship("User", back_populates="audit_logs")


# this represents one row in the final Technical Documentation table
class ETDRow(Base):
    __tablename__ = "etd_rows"
    # Fix 1.1: Unique constraint prevents duplicate rows from concurrent inserts
    __table_args__ = (
        UniqueConstraint(
            "device_id", "gspr_requirement_id",
            name="uq_etd_device_gspr"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("device_profiles.id"))
    gspr_requirement_id = Column(Integer, ForeignKey("gspr_requirements.id"))
    applicability = Column(String)  # 'Applicable' or 'Not Applicable'
    notes = Column(Text)
    created_by = Column(String)
    updated_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    device = relationship("DeviceProfile", back_populates="etd_rows")
    gspr_requirement = relationship("GSPRRequirement", back_populates="etd_rows")
    standards = relationship("Standard", secondary=etd_row_standards, back_populates="etd_rows")
    evidence_documents = relationship("EvidenceDocument", secondary=etd_row_evidence, back_populates="etd_rows")


# tracks files that were uploaded for processing
class ImportDocument(Base):
    __tablename__ = "import_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(String, index=True) # MDR, STANDARD, or EVIDENCE
    original_filename = Column(String)
    stored_path = Column(String)
    sha256 = Column(String, unique=True, index=True) # to prevent duplicate uploads
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, server_default=func.now())
    parse_status = Column(String, default="pending")
    parse_error = Column(Text)
    parse_warnings = Column(String, default="[]")
    parsed_json_path = Column(String)
    
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=True)

    user = relationship("User")
    standard = relationship("Standard")
