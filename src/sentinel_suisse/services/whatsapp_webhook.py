"""Meta WhatsApp Cloud API webhook helpers (Phase 23+)."""

from __future__ import annotations

import hashlib
import hmac
import logging
import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.models.enums import ChannelType
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.security.pii import decrypt_pii

logger = logging.getLogger(__name__)


class WhatsAppWebhookError(ValueError):
    """Invalid webhook challenge or signature."""


def normalize_wa_id(value: str) -> str:
    return re.sub(r"\D", "", value)


def verify_subscription_challenge(
    settings: Settings,
    *,
    hub_mode: str | None,
    hub_verify_token: str | None,
    hub_challenge: str | None,
) -> str:
    """Respond to Meta's GET webhook verification handshake."""
    if not settings.whatsapp_verify_token:
        msg = "WHATSAPP_VERIFY_TOKEN is not configured"
        raise WhatsAppWebhookError(msg)
    if hub_mode != "subscribe":
        msg = "hub.mode must be subscribe"
        raise WhatsAppWebhookError(msg)
    if not hub_challenge:
        msg = "hub.challenge is required"
        raise WhatsAppWebhookError(msg)
    if not hub_verify_token or not hmac.compare_digest(
        hub_verify_token, settings.whatsapp_verify_token
    ):
        msg = "hub.verify_token mismatch"
        raise WhatsAppWebhookError(msg)
    return hub_challenge


def verify_request_signature(
    settings: Settings,
    *,
    body: bytes,
    signature_header: str | None,
) -> None:
    """Validate X-Hub-Signature-256 from Meta (required when app secret is set)."""
    if not settings.whatsapp_app_secret:
        logger.warning("WHATSAPP_APP_SECRET unset — skipping signature check")
        return
    if not signature_header or not signature_header.startswith("sha256="):
        msg = "Missing or invalid X-Hub-Signature-256"
        raise WhatsAppWebhookError(msg)
    digest = hmac.new(
        settings.whatsapp_app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    expected = f"sha256={digest}"
    if not hmac.compare_digest(expected, signature_header):
        msg = "X-Hub-Signature-256 mismatch"
        raise WhatsAppWebhookError(msg)


def extract_inbound_sender_ids(payload: dict[str, Any]) -> list[str]:
    """Collect WhatsApp `from` ids from inbound message events (digits only)."""
    senders: list[str] = []
    entries = payload.get("entry")
    if not isinstance(entries, list):
        return senders
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        changes = entry.get("changes")
        if not isinstance(changes, list):
            continue
        for change in changes:
            if not isinstance(change, dict):
                continue
            value = change.get("value")
            if not isinstance(value, dict):
                continue
            messages = value.get("messages")
            if not isinstance(messages, list):
                continue
            for message in messages:
                if not isinstance(message, dict):
                    continue
                sender = message.get("from")
                if sender:
                    senders.append(normalize_wa_id(str(sender)))
    return senders


def auto_verify_whatsapp_senders(db: Session, sender_ids: list[str]) -> int:
    """Mark unverified WhatsApp channels verified when sender matches stored phone."""
    if not sender_ids:
        return 0
    sender_set = set(sender_ids)
    channels = db.scalars(
        select(NotificationChannel).where(
            NotificationChannel.channel_type == ChannelType.WHATSAPP,
            NotificationChannel.is_verified.is_(False),
        )
    ).all()
    verified = 0
    now = datetime.now(UTC)
    for channel in channels:
        try:
            plain = decrypt_pii(channel.channel_address)
        except ValueError:
            logger.warning("Skipping channel_id=%s — PII decrypt failed", channel.id)
            continue
        if normalize_wa_id(plain) in sender_set:
            channel.is_verified = True
            channel.verified_at = now
            verified += 1
    if verified:
        db.commit()
    return verified


def summarize_webhook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a PII-safe summary of an inbound webhook payload."""
    object_name = payload.get("object")
    entries = payload.get("entry")
    entry_count = len(entries) if isinstance(entries, list) else 0
    message_count = 0
    status_count = 0
    if isinstance(entries, list):
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            changes = entry.get("changes")
            if not isinstance(changes, list):
                continue
            for change in changes:
                if not isinstance(change, dict):
                    continue
                value = change.get("value")
                if not isinstance(value, dict):
                    continue
                messages = value.get("messages")
                statuses = value.get("statuses")
                if isinstance(messages, list):
                    message_count += len(messages)
                if isinstance(statuses, list):
                    status_count += len(statuses)
    return {
        "object": object_name,
        "entry_count": entry_count,
        "message_count": message_count,
        "status_count": status_count,
    }
