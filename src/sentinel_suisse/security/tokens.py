"""API token generation and verification."""

import secrets

import bcrypt


def generate_api_token() -> str:
    return secrets.token_urlsafe(32)


def hash_api_token(token: str) -> str:
    return bcrypt.hashpw(token.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_api_token(token: str, token_hash: str) -> bool:
    try:
        return bcrypt.checkpw(token.encode("utf-8"), token_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
