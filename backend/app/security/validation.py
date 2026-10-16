"""
security/validation.py
======================
Server-side sanitisation and validation helpers for auth inputs.

Rules enforced here (independent of any front-end checks):
  - HTML / script-tag stripping via bleach
  - SQL meta-character removal from non-password fields
  - Structured WARNING-level logging of validation failures
    (only logs route + IP + timestamp; never the bad value itself)
"""

import re
import logging
import bleach
from typing import Optional

# ---------------------------------------------------------------------------
# Module logger -- writes to the application log file / stdout.
# Log messages deliberately omit the actual bad input and the specific field
# name to avoid leaking data or hinting at which checks are in place.
# ---------------------------------------------------------------------------
logger = logging.getLogger("gspr.security.validation")


# ---------------------------------------------------------------------------
# Sanitisation helpers
# ---------------------------------------------------------------------------

# SQL meta-characters that have no place in an email or display-name field.
# Passwords are NOT run through this function -- only their *length* is capped.
_SQL_METACHAR_RE = re.compile(
    r"(--|;|/\*|\*/|xp_|exec\s|union\s|select\s|insert\s|drop\s|"
    r"alter\s|delete\s|update\s|cast\s*\(|convert\s*\()",
    re.IGNORECASE,
)


def sanitize_text(value: str, max_length: int = 255) -> str:
    """
    Strip HTML/script tags and remove SQL meta-characters from a text field
    such as a display name.

    - Runs bleach.clean() to strip all tags (strip=True removes them entirely).
    - Removes known SQL injection fragments (for defence-in-depth; the ORM
      already uses parameterised queries, so this is an extra safety belt).
    - Truncates to max_length.
    - Returns the sanitised string.
    """
    if not isinstance(value, str):
        return ""

    # 1. Strip HTML / script tags
    cleaned = bleach.clean(value, tags=[], attributes={}, strip=True)

    # 2. Strip SQL meta-characters
    cleaned = _SQL_METACHAR_RE.sub("", cleaned)

    # 3. Normalise whitespace and enforce length cap
    cleaned = cleaned.strip()[:max_length]

    return cleaned


def sanitize_email(value: str, max_length: int = 254) -> str:
    """
    Normalise an email-like string: strip whitespace, lowercase, truncate.
    Full format validation is handled by Pydantic's EmailStr -- this just
    ensures the raw bytes that arrive are safe before Pydantic sees them.
    """
    if not isinstance(value, str):
        return ""
    # Strip HTML first (someone might try '<script>@bec-robotics.com')
    cleaned = bleach.clean(value, tags=[], attributes={}, strip=True)
    return cleaned.strip().lower()[:max_length]


def sanitize_password(value: str, max_length: int = 128) -> str:
    """
    Passwords are NOT stripped of special characters (they need them for
    strength). We only enforce a hard upper-length limit to prevent bcrypt
    DoS (bcrypt silently truncates at 72 bytes; huge inputs just waste CPU).

    No HTML sanitisation -- a password may legitimately contain '<', '>' etc.
    """
    if not isinstance(value, str):
        return ""
    return value[:max_length]


# ---------------------------------------------------------------------------
# Validation failure logger
# ---------------------------------------------------------------------------

def log_validation_failure(
    route: str,
    client_ip: Optional[str],
    reason: str = "Schema validation failed",
) -> None:
    """
    Record a server-side validation failure.

    Deliberately does NOT log:
      - The actual submitted value (avoid logging PII / attack payloads)
      - Which specific field failed (avoid hinting at internal field names)

    Args:
        route:      e.g. "/auth/register"
        client_ip:  IP address of the requester (from request.client.host)
        reason:     Brief category label, e.g. "Schema validation failed"
    """
    logger.warning(
        "[AUTH-VALIDATION] route=%s ip=%s reason=%s",
        route,
        client_ip or "unknown",
        reason,
    )
