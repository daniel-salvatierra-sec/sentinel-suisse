"""Signed tokens for email channel verification (no DB storage)."""

import base64
import hashlib
import hmac
import json
import time
from typing import Any


class VerificationTokenError(ValueError):
    """Invalid or expired verification token."""


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_channel_verification_token(
    *,
    channel_id: int,
    user_id: int,
    secret: str,
    ttl_hours: int,
) -> str:
    payload = {
        "cid": channel_id,
        "uid": user_id,
        "exp": int(time.time()) + ttl_hours * 3600,
    }
    body = _b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def _decode_and_verify(token: str, secret: str) -> dict[str, Any]:
    try:
        body, signature = token.split(".", 1)
    except ValueError as exc:
        raise VerificationTokenError("Malformed token") from exc

    expected = hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise VerificationTokenError("Invalid token signature")

    try:
        payload = json.loads(_b64_decode(body))
    except (json.JSONDecodeError, ValueError) as exc:
        raise VerificationTokenError("Invalid token payload") from exc

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise VerificationTokenError("Token expired")

    return payload


def parse_channel_verification_token(token: str, secret: str) -> dict[str, Any]:
    payload = _decode_and_verify(token, secret)

    channel_id = payload.get("cid")
    user_id = payload.get("uid")
    if not isinstance(channel_id, int) or not isinstance(user_id, int):
        raise VerificationTokenError("Invalid token claims")

    return {"channel_id": channel_id, "user_id": user_id}


def create_login_token(*, user_id: int, secret: str, ttl_minutes: int) -> str:
    """Signed, short-lived token for the passwordless magic-login flow."""
    payload = {
        "typ": "login",
        "uid": user_id,
        "exp": int(time.time()) + ttl_minutes * 60,
    }
    body = _b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def parse_login_token(token: str, secret: str) -> int:
    """Return the user_id encoded in a magic-login token, or raise."""
    payload = _decode_and_verify(token, secret)

    if payload.get("typ") != "login":
        raise VerificationTokenError("Invalid token type")

    user_id = payload.get("uid")
    if not isinstance(user_id, int):
        raise VerificationTokenError("Invalid token claims")

    return user_id
