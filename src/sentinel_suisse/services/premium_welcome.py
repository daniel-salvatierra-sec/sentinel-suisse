"""Transactional mail after Premium is activated — never blocks billing."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.i18n.premium import format_premium_welcome
from sentinel_suisse.models.user import User
from sentinel_suisse.security.pii import decrypt_pii

logger = logging.getLogger(__name__)


def send_premium_welcome(user: User, settings: Settings | None = None) -> None:
    cfg = settings or get_settings()
    try:
        email = decrypt_pii(user.email)
    except Exception:
        logger.warning("premium welcome: could not decrypt email user_id=%s", user.id)
        return
    subject, body = format_premium_welcome(user.locale, cfg.public_app_url)
    use_smtp = cfg.smtp_is_configured() and cfg.notifier_mode in ("auto", "smtp")
    if use_smtp:
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = cfg.smtp_from
            message["To"] = email
            message.set_content(body)
            with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=30) as smtp:
                if cfg.smtp_use_tls:
                    smtp.starttls()
                if cfg.smtp_user:
                    smtp.login(cfg.smtp_user, cfg.smtp_password)
                smtp.send_message(message)
            return
        except smtplib.SMTPException as exc:
            logger.warning("premium welcome SMTP failed user_id=%s: %s", user.id, exc)
    logger.info("PREMIUM WELCOME to=%s subject=%s", email, subject)
