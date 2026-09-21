"""Email+password login, forgot/set-password, and legacy magic-link confirm."""

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.i18n.login import format_set_password_email
from sentinel_suisse.models.user import User
from sentinel_suisse.notifications.email_html import build_html_email
from sentinel_suisse.security.passwords import (
    hash_password,
    validate_password_strength,
    verify_password,
)
from sentinel_suisse.security.pii import email_lookup
from sentinel_suisse.security.tokens import generate_api_token, hash_api_token
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_device_trust_token,
    create_set_password_token,
    parse_login_token,
    parse_set_password_token,
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


@dataclass
class LoginAttemptResult:
    session: MagicLoginResult | None = None
    needs_password: bool = False
    invalid_credentials: bool = False
    sent_reset: bool = False


def _secret(settings: Settings) -> str:
    secret = settings.secret_key or settings.pii_encryption_key
    if not secret:
        msg = "SECRET_KEY or PII_ENCRYPTION_KEY required for login tokens"
        raise RuntimeError(msg)
    return secret


def issue_session(user: User, settings: Settings) -> MagicLoginResult:
    api_key = generate_api_token()
    user.api_token_hash = hash_api_token(api_key)
    device_token = create_device_trust_token(user_id=user.id, secret=_secret(settings))
    return MagicLoginResult(user=user, api_key=api_key, device_token=device_token)


def make_device_trust_for_user(user_id: int, settings: Settings) -> str:
    return create_device_trust_token(user_id=user_id, secret=_secret(settings))


def _send_email(settings: Settings, *, to: str, subject: str, body: str, url: str) -> None:
    use_smtp = settings.smtp_is_configured() and settings.notifier_mode in ("auto", "smtp")
    if use_smtp:
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = settings.smtp_from
            message["To"] = to
            message.set_content(body)
            message.add_alternative(build_html_email(body, url), subtype="html")
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
            return
        except smtplib.SMTPException as exc:
            logger.warning("Login/set-password SMTP failed, logging URL instead: %s", exc)
    logger.info("AUTH EMAIL to=%s url=%s subject=%s", to, url, subject)


def request_set_password_email(
    db: Session,
    settings: Settings,
    email: str,
    locale: str,
) -> None:
    lookup = email_lookup(email.strip().lower())
    user = db.scalar(select(User).where(User.email_lookup == lookup, User.is_active.is_(True)))
    if user is None:
        logger.info("set-password requested for unknown email")
        return
    token = create_set_password_token(
        user_id=user.id,
        secret=_secret(settings),
        ttl_minutes=settings.login_token_ttl_minutes,
    )
    url = f"{settings.public_app_url.rstrip('/')}/?setpw={token}"
    subject, body = format_set_password_email(
        locale,
        url,
        ttl_minutes=settings.login_token_ttl_minutes,
    )
    _send_email(settings, to=email, subject=subject, body=body, url=url)


def request_magic_login(
    db: Session,
    settings: Settings,
    email: str,
    locale: str,
    *,
    password: str | None = None,
    device_token: str | None = None,
) -> LoginAttemptResult:
    """Authenticate with email+password; legacy accounts get a set-password email."""
    del device_token  # reserved; password is the auth factor
    lookup = email_lookup(email.strip().lower())
    user = db.scalar(select(User).where(User.email_lookup == lookup, User.is_active.is_(True)))
    if user is None:
        # Same generic shape as wrong password — no account leak.
        return LoginAttemptResult(invalid_credentials=True)

    if not user.password_hash:
        request_set_password_email(db, settings, email, locale)
        return LoginAttemptResult(needs_password=True, sent_reset=True)

    if not password or not verify_password(password, user.password_hash):
        return LoginAttemptResult(invalid_credentials=True)

    result = issue_session(user, settings)
    db.commit()
    db.refresh(user)
    logger.info("password login ok user_id=%s", user.id)
    return LoginAttemptResult(session=result)


def confirm_magic_login(db: Session, settings: Settings, token: str) -> MagicLoginResult:
    """Legacy magic-link confirm (still accepted for old emails)."""
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


def set_password_with_token(
    db: Session,
    settings: Settings,
    token: str,
    password: str,
) -> MagicLoginResult:
    err = validate_password_strength(password)
    if err:
        raise MagicLoginError(err, err)
    try:
        user_id = parse_set_password_token(token, _secret(settings))
    except VerificationTokenError as exc:
        raise MagicLoginError("invalid_token", str(exc)) from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise MagicLoginError("user_not_found", "Account not found or inactive.")

    user.password_hash = hash_password(password)
    result = issue_session(user, settings)
    db.commit()
    db.refresh(user)
    return result
