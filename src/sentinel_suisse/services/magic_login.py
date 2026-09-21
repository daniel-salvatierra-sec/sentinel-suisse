"""Passwordless login for returning users.

Known accounts sign in with email only (rate-limited). A long-lived
device-trust token is still issued so the same browser can reconnect
even faster after "Sign out". Magic-link confirm remains for old emails
already in flight.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.models.user import User
from sentinel_suisse.security.pii import email_lookup
from sentinel_suisse.security.tokens import generate_api_token, hash_api_token
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_device_trust_token,
    parse_device_trust_token,
    parse_login_token,
)

logger = logging.getLogger(__name__)


class MagicLoginError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass
class MagicLoginResult:
    user: User
    api_key: str
    device_token: str


def _secret(settings: Settings) -> str:
    secret = settings.secret_key or settings.pii_encryption_key
    if not secret:
        msg = "SECRET_KEY or PII_ENCRYPTION_KEY required for login tokens"
        raise RuntimeError(msg)
    return secret


def issue_session(user: User, settings: Settings) -> MagicLoginResult:
    """Mint a fresh API key + device-trust token for this user."""
    api_key = generate_api_token()
    user.api_token_hash = hash_api_token(api_key)
    device_token = create_device_trust_token(user_id=user.id, secret=_secret(settings))
    return MagicLoginResult(user=user, api_key=api_key, device_token=device_token)


def try_device_trust_login(
    db: Session,
    settings: Settings,
    email: str,
    device_token: str | None,
) -> MagicLoginResult | None:
    """If device_token matches this email's account, issue a session."""
    if not device_token:
        return None
    lookup = email_lookup(email.strip().lower())
    user = db.scalar(select(User).where(User.email_lookup == lookup, User.is_active.is_(True)))
    if user is None:
        return None
    try:
        trusted_uid = parse_device_trust_token(device_token, _secret(settings))
    except VerificationTokenError:
        return None
    if trusted_uid != user.id:
        return None
    result = issue_session(user, settings)
    db.commit()
    db.refresh(user)
    return result


def request_magic_login(
    db: Session,
    settings: Settings,
    email: str,
    locale: str,
    *,
    device_token: str | None = None,
) -> MagicLoginResult | None:
    """Sign in a known account with email only (no inbox click).

    Unknown emails still get a generic success with no session, so we do
    not reveal which addresses have an account.
    """
    del locale  # kept for API compatibility / future locale-aware notices
    trusted = try_device_trust_login(db, settings, email, device_token)
    if trusted is not None:
        return trusted

    lookup = email_lookup(email.strip().lower())
    user = db.scalar(select(User).where(User.email_lookup == lookup, User.is_active.is_(True)))
    if user is None:
        logger.info("login requested for unknown email")
        return None

    result = issue_session(user, settings)
    db.commit()
    db.refresh(user)
    logger.info("email login ok user_id=%s", user.id)
    return result


def confirm_magic_login(db: Session, settings: Settings, token: str) -> MagicLoginResult:
    """Validate a legacy magic-login token and issue a fresh session."""
    try:
        user_id = parse_login_token(token, _secret(settings))
    except VerificationTokenError as exc:
        raise MagicLoginError("invalid_token", str(exc)) from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise MagicLoginError("user_not_found", "Account not found or inactive.")

    result = issue_session(user, settings)
    db.commit()
    db.refresh(user)
    return result


def make_device_trust_for_user(user_id: int, settings: Settings) -> str:
    return create_device_trust_token(user_id=user_id, secret=_secret(settings))
