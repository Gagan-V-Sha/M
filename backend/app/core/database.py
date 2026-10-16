"""
core/database.py
================
SQLAlchemy engine setup and session factory.

Changes from audit:
  - Finding 3.4: SQLite WAL mode enabled on connect (concurrent reads,
    serialised writes — no more "database is locked" crashes).
    Also sets NORMAL synchronous and 10k page cache for better performance.
  - The engine now auto-detects whether it is targeting SQLite or PostgreSQL
    and only applies SQLite PRAGMAs when appropriate.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BACKEND_ROOT, "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "data.db")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

_is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

# Build engine with appropriate settings per DB backend
if _is_sqlite:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_wal(dbapi_conn, _connection_record):
        """
        Enable WAL journal mode on every new SQLite connection.
        WAL allows multiple concurrent readers + one writer without locking.
        NORMAL synchronous is safe with WAL and much faster than FULL.
        """
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

else:
    # PostgreSQL — no SQLite-specific connect_args needed
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables():
    from app.core.models import (
        Standard, GSPRRequirement, StandardGSPRMapping, DeviceProfile,
        StandardApplicabilityRule, EvidenceDocument, User, AuditLog,
        ETDRow, etd_row_standards, etd_row_evidence, ImportDocument,
    )
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    print("Database tables have been created successfully.")
