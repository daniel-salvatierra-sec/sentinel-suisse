"""Passwordless "magic link" login for returning users.

Users who lose their locally-stored API key (new device, cleared storage,
etc.) have no other way back into their account. This lets them request a
short-lived, signed link by email that mints them a fresh API key.

After the first successful login on a browser, a long-lived device-trust
token lets them reconnect with the same email without another inbox click.
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
from sentinel_suisse.notifications.email_html import build_html_email
from sentinel_suisse.security.pii import email_lookup
from sentinel_suisse.security.tokens import generate_api_token, hash_api_token
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_device_trust_token,
    create_login_token,
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


def build_login_url(settings: Settings, token: str) -> str:
    base = settings.public_app_url.rstrip("/")
    return f"{base}/?login={token}"


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
    """If device_token matches this email's account, issue a session without email."""
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
    """Send a login link, or reconnect instantly with a valid device-trust token.

    Always succeeds silently for unknown emails so we don't reveal which
    addresses have an account. Returns a session when device trust works.
    """
    trusted = try_device_trust_login(db, settings, email, device_token)
    if trusted is not None:
        return trusted

    lookup = email_lookup(email.strip().lower())
    user = db.scalar(select(User).where(User.email_lookup == lookup, User.is_active.is_(True)))
    if user is None:
        logger.info("magic login requested for unknown email")
        return None

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
            message.add_alternative(build_html_email(body, url), subtype="html")
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
            return None
        except smtplib.SMTPException as exc:
            logger.warning("Magic login SMTP failed, logging URL instead: %s", exc)

    logger.info("MAGIC LOGIN EMAIL to=%s url=%s", email, url)
    return None


def confirm_magic_login(db: Session, settings: Settings, token: str) -> MagicLoginResult:
    """Validate a login token and issue a fresh API key for the user."""
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
