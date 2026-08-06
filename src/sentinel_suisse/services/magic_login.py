"""Passwordless "magic link" login for returning users.

Users who lose their locally-stored API key (new device, cleared storage,
etc.) have no other way back into their account. This lets them request a
short-lived, signed link by email that mints them a fresh API key.
"""

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.i18n.login import format_login_email
from sentinel_suisse.models.user import User
from sentinel_suisse.security.pii import email_lookup
from sentinel_suisse.security.tokens import generate_api_token, hash_api_token
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_login_token,
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


def _secret(settings: Settings) -> str:
    secret = settings.secret_key or settings.pii_encryption_key
    if not secret:
        msg = "SECRET_KEY or PII_ENCRYPTION_KEY required for login tokens"
        raise RuntimeError(msg)
    return secret


def build_login_url(settings: Settings, token: str) -> str:
    base = settings.public_app_url.rstrip("/")
    return f"{base}/?login={token}"


def request_magic_login(db: Session, settings: Settings, email: str, locale: str) -> None:
    """Send a login link if the email matches an active account.

    Always succeeds silently for unknown emails so we don't reveal which
    addresses have an account.
    """
    lookup = email_lookup(email.strip().lower())
    user = db.scalar(select(User).where(User.email_lookup == lookup, User.is_active.is_(True)))
    if user is None:
        logger.info("magic login requested for unknown email")
        return

    token = create_login_token(
        user_id=user.id,
        secret=_secret(settings),
        ttl_minutes=settings.login_token_ttl_minutes,
    )
    url = build_login_url(settings, token)
    subject, body = format_login_email(
        locale,
        url,
        ttl_minutes=settings.login_token_ttl_minutes,
    )

    use_smtp = settings.smtp_is_configured() and settings.notifier_mode in ("auto", "smtp")
    if use_smtp:
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = settings.smtp_from
            message["To"] = email
            message.set_content(body)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
            return
        except smtplib.SMTPException as exc:
            logger.warning("Magic login SMTP failed, logging URL instead: %s", exc)

    logger.info("MAGIC LOGIN EMAIL to=%s url=%s", email, url)


def confirm_magic_login(db: Session, settings: Settings, token: str) -> MagicLoginResult:
    """Validate a login token and issue a fresh API key for the user."""
    try:
        user_id = parse_login_token(token, _secret(settings))
    except VerificationTokenError as exc:
        raise MagicLoginError("invalid_token", str(exc)) from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise MagicLoginError("user_not_found", "Account not found or inactive.")

    api_key = generate_api_token()
    user.api_token_hash = hash_api_token(api_key)
    db.commit()
    db.refresh(user)

    return MagicLoginResult(user=user, api_key=api_key)
