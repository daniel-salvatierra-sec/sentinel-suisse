"""User password hashing (bcrypt)."""

from __future__ import annotations

import bcrypt

MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 128


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def validate_password_strength(password: str) -> str | None:
    """Return an error code or None if OK."""
    if len(password) < MIN_PASSWORD_LEN:
        return "password_too_short"
    if len(password) > MAX_PASSWORD_LEN:
        return "password_too_long"
    return None
