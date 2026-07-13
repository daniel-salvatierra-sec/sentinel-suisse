"""Send and apply email verification for notification channels."""

import logging
import smtplib
from datetime import UTC, datetime
from email.message import EmailMessage

from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.i18n.verification import format_verification_email
from sentinel_suisse.models.enums import ChannelType
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.security.verification_tokens import (
    VerificationTokenError,
    create_channel_verification_token,
    parse_channel_verification_token,
)

logger = logging.getLogger(__name__)


def _verification_secret(settings: Settings) -> str:
    secret = settings.secret_key or settings.pii_encryption_key
    if not secret:
        msg = "SECRET_KEY or PII_ENCRYPTION_KEY required for verification tokens"
        raise RuntimeError(msg)
    return secret


def build_verification_url(settings: Settings, token: str) -> str:
    base = settings.public_app_url.rstrip("/")
    return f"{base}/?verify={token}"


def send_channel_verification_email(
    settings: Settings,
    *,
    email: str,
    locale: str,
    channel_id: int,
    user_id: int,
) -> str:
    token = create_channel_verification_token(
        channel_id=channel_id,
        user_id=user_id,
        secret=_verification_secret(settings),
        ttl_hours=settings.verification_token_ttl_hours,
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


def verify_email_channel(db: Session, token: str) -> NotificationChannel:
    settings = get_settings()
    try:
        claims = parse_channel_verification_token(token, _verification_secret(settings))
    except VerificationTokenError as exc:
        raise ValueError(str(exc)) from exc

    channel = db.get(NotificationChannel, claims["channel_id"])
    if channel is None or channel.user_id != claims["user_id"]:
        raise ValueError("Channel not found")

    if channel.channel_type != ChannelType.EMAIL:
        raise ValueError("Invalid channel type")

    if not channel.is_verified:
        channel.is_verified = True
        channel.verified_at = datetime.now(UTC)
        db.commit()
        db.refresh(channel)

    return channel
