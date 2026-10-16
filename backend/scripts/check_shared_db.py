"""
Verify DATABASE_URL is reachable and print a safe summary (no password).

Usage (from backend/):
  python scripts/check_shared_db.py
"""

from __future__ import annotations

import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def _redact(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "?"
        port = parsed.port or ""
        db = (parsed.path or "/").lstrip("/") or "?"
        user = parsed.username or "?"
        port_bit = f":{port}" if port else ""
        return f"{parsed.scheme}://{user}:***@{host}{port_bit}/{db}"
    except Exception:
        return "(unparseable DATABASE_URL)"


def main() -> int:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        print("DATABASE_URL is not set.")
        return 1

    print("DATABASE_URL:", _redact(url))
    if not url.lower().startswith("postgres"):
        print("Backend: SQLite (or non-Postgres). Shared Pi+workstation mode needs PostgreSQL.")
        return 0

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            conn.execute(text("SELECT 1"))
        print("Connection: OK")
        print("Server:", (version or "")[:80])
        return 0
    except Exception as exc:
        print("Connection: FAILED")
        print(exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
