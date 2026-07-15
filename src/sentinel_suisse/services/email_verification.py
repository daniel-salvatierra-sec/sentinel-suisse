"""Send and apply channel verification (email + WhatsApp)."""

import logging
import re
import smtplib
from datetime import UTC, datetime
from email.message import EmailMessage

import httpx
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.i18n.verification import (
    format_verification_email,
    format_verification_whatsapp,
)
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_channel_verification_token,
    parse_channel_verification_token,
)

logger = logging.getLogger(__name__)

_GRAPH_API_VERSION = "v21.0"


def _verification_secret(settings: Settings) -> str:
    secret = settings.secret_key or settings.pii_encryption_key
    if not secret:
        msg = "SECRET_KEY or PII_ENCRYPTION_KEY required for verification tokens"
        raise RuntimeError(msg)
    return secret


def _normalize_whatsapp_phone(address: str) -> str:
    return re.sub(r"\D", "", address)


def build_verification_url(settings: Settings, token: str) -> str:
    base = settings.public_app_url.rstrip("/")
    return f"{base}/?verify={token}"


def _create_verification_token(
    settings: Settings,
    *,
    channel_id: int,
    user_id: int,
) -> str:
    return create_channel_verification_token(
        channel_id=channel_id,
        user_id=user_id,
        secret=_verification_secret(settings),
        ttl_hours=settings.verification_token_ttl_hours,
    )


def send_channel_verification_email(
    settings: Settings,
    *,
    email: str,
    locale: str,
    channel_id: int,
    user_id: int,
) -> str:
    token = _create_verification_token(
        settings,
        channel_id=channel_id,
        user_id=user_id,
    )
    url = build_verification_url(settings, token)
    subject, body = format_verification_email(
        locale,
        url,
        ttl_hours=settings.verification_token_ttl_hours,
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
            return token
        except smtplib.SMTPException as exc:
            logger.warning("Verification SMTP failed, logging URL instead: %s", exc)

    logger.info("VERIFICATION EMAIL to=%s url=%s", email, url)
    return token


def send_channel_verification_whatsapp(
    settings: Settings,
    *,
    phone: str,
    locale: str,
    channel_id: int,
    user_id: int,
) -> str:
    token = _create_verification_token(
        settings,
        channel_id=channel_id,
        user_id=user_id,
    )
    url = build_verification_url(settings, token)
    body = format_verification_whatsapp(
        locale,
        url,
        ttl_hours=settings.verification_token_ttl_hours,
        keyword=settings.whatsapp_verify_keyword,
    )
    normalized = _normalize_whatsapp_phone(phone)
    if not normalized:
        msg = "Invalid WhatsApp phone number"
        raise ValueError(msg)

    if settings.whatsapp_is_configured():
        try:
            api_url = (
                f"https://graph.facebook.com/{_GRAPH_API_VERSION}/"
                f"{settings.whatsapp_phone_number_id}/messages"
            )
            response = httpx.post(
                api_url,
                headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": normalized,
                    "type": "text",
                    "text": {"body": body},
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return token
        except httpx.HTTPError as exc:
            logger.warning("Verification WhatsApp failed, logging URL instead: %s", exc)

    logger.info("VERIFICATION WHATSAPP to=%s url=%s", phone, url)
    return token


def verify_channel_by_token(db: Session, token: str) -> NotificationChannel:
    settings = get_settings()
    try:
        claims = parse_channel_verification_token(token, _verification_secret(settings))
    except VerificationTokenError as exc:
        raise ValueError(str(exc)) from exc

    channel = db.get(NotificationChannel, claims["channel_id"])
    if channel is None or channel.user_id != claims["user_id"]:
        raise ValueError("Channel not found")

    if not channel.is_verified:
        channel.is_verified = True
        channel.verified_at = datetime.now(UTC)
        db.commit()
        db.refresh(channel)

    return channel


def verify_email_channel(db: Session, token: str) -> NotificationChannel:
    """Backward-compatible alias for email verification links."""
    return verify_channel_by_token(db, token)
