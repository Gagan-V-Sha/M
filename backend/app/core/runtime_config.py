"""
Deploy roles for Pi (runtime) vs workstation (scanner).

Same codebase; different env:
  ROLE=runtime  MINERU_ENABLED=false   → Pi / always-on app
  ROLE=scanner  MINERU_ENABLED=true    → workstation scans (default)
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# Load .env before reading flags (main.py may import this module before load_dotenv()).
load_dotenv()


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# Default True so existing workstation installs keep scanning without .env changes.
MINERU_ENABLED: bool = _env_flag("MINERU_ENABLED", default=True)

_role = (os.getenv("ROLE") or "").strip().lower()
if _role in ("runtime", "scanner"):
    ROLE: str = _role
else:
    ROLE = "scanner" if MINERU_ENABLED else "runtime"


def database_backend() -> str:
    """sqlite | postgresql | other — never returns credentials."""
    url = (os.getenv("DATABASE_URL") or "").strip().lower()
    if url.startswith("postgres"):
        return "postgresql"
    if url.startswith("sqlite") or not url:
        return "sqlite"
    return "other"


def public_runtime_config(mineru_available: bool, mineru_version: str) -> dict:
    """Payload for GET /config — frontend uses this to hide scan UI on the Pi."""
    ready = bool(MINERU_ENABLED and mineru_available)
    db_backend = database_backend()
    return {
        "role": ROLE,
        "mineru_enabled": MINERU_ENABLED,
        "mineru_available": mineru_available,
        "mineru_ready": ready,
        "mineru_version": mineru_version if ready else None,
        "database_backend": db_backend,
        "database_shared": db_backend == "postgresql",
        "message": (
            None
            if ready
            else (
                "PDF scanning is disabled on this host. "
                "Use the workstation with MINERU_ENABLED=true; mappings appear here via the shared database."
            )
        ),
    }
