"""
security/auth.py
================
Authentication helpers: JWT creation/verification, password hashing, and
the FastAPI dependency that protects routes.

Changes from audit:
  - Finding 4.1: SECRET_KEY now raises RuntimeError at startup if missing
    or shorter than 32 chars. The old fallback to "supersecretkey" is gone.
  - Finding 10.4: python-jose replaced with PyJWT (maintained, no CVEs).
  - Finding 8.1: get_current_user accepts tokens from both Bearer header
    and the httpOnly 'access_token' cookie so all existing API clients
    (Swagger, tests) and the new cookie-based frontend both work.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt as pyjwt                      # PyJWT — replaces python-jose
from jwt.exceptions import InvalidTokenError
import bcrypt
import os
import re
from dotenv import load_dotenv

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import models

load_dotenv()

# ---------------------------------------------------------------------------
# Security configuration
# ---------------------------------------------------------------------------

_raw_key = os.getenv("SECRET_KEY", "")
if not _raw_key or len(_raw_key) < 32:
    raise RuntimeError(
        "SECRET_KEY environment variable is missing or too short (minimum 32 chars). "
        "Generate one with:\n"
        "  python -c \"import secrets; print(secrets.token_urlsafe(64))\"\n"
        "Then set it in your .env file."
    )

SECRET_KEY: str = _raw_key
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme — used by Swagger UI and API clients that send Bearer headers.
# auto_error=False so we can fall back to the cookie without raising 401 first.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def validate_password_strength(password: str) -> None:
    """Enforce password complexity rules."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if " " in password:
        raise ValueError("Password must not contain spaces")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must have at least one capital letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must have at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must have at least one number")
    if not re.search(r"""[!@#$%^&*()?\":{}|<>\-_+=\[\]~\\,.]""", password):
        raise ValueError("Password must have a special character (like ! or @)")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt.  Guards against bcrypt DoS (128-char cap)."""
    if len(password) > 128:
        raise ValueError("Password exceeds maximum allowed length")
    validate_password_strength(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=60)
    )
    to_encode["exp"] = expire
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# FastAPI dependency — get the currently authenticated user
# Accepts token from:
#   1. httpOnly cookie 'access_token'  (browser frontend)
#   2. Authorization: Bearer <token>   (Swagger UI / API clients / tests)
# ---------------------------------------------------------------------------

def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Prefer the httpOnly cookie; fall back to Authorization header
    raw_token: Optional[str] = request.cookies.get("access_token") or bearer_token

    if not raw_token:
        raise credentials_exception

    try:
        payload = pyjwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can do this")
    return current_user


def get_current_admin_or_editor(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role not in ("admin", "editor"):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
