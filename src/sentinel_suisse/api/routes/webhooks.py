"""WhatsApp Cloud API webhook routes (Meta callback)."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.services.whatsapp_webhook import (
    WhatsAppWebhookError,
    auto_verify_whatsapp_senders,
    extract_inbound_sender_ids,
    summarize_webhook_payload,
    verify_request_signature,
    verify_subscription_challenge,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/whatsapp", tags=["webhooks"])


def _settings() -> Settings:
    return get_settings()


@router.get("")
@limiter.limit("30/minute")
def whatsapp_webhook_verify(
    request: Request,
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
    settings: Settings = Depends(_settings),
) -> Response:
    """Meta subscription verification (returns hub.challenge as plain text)."""
    try:
        challenge = verify_subscription_challenge(
            settings,
            hub_mode=hub_mode,
            hub_verify_token=hub_verify_token,
            hub_challenge=hub_challenge,
        )
    except WhatsAppWebhookError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return Response(content=challenge, media_type="text/plain")


@router.post("")
@limiter.limit("60/minute")
async def whatsapp_webhook_receive(
    request: Request,
    settings: Settings = Depends(_settings),
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    """Acknowledge Meta webhook events; auto-verify matching WhatsApp channels."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    try:
        verify_request_signature(settings, body=body, signature_header=signature)
    except WhatsAppWebhookError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload must be a JSON object",
        )

    summary = summarize_webhook_payload(payload)
    logger.info(
        "whatsapp_webhook object=%s entries=%s messages=%s statuses=%s",
        summary.get("object"),
        summary.get("entry_count"),
        summary.get("message_count"),
        summary.get("status_count"),
    )

    verified = 0
    if settings.whatsapp_inbound_auto_verify:
        senders = extract_inbound_sender_ids(
            payload,
            keyword=settings.whatsapp_verify_keyword,
        )
        verified = auto_verify_whatsapp_senders(db, senders)
        if verified:
            logger.info("whatsapp_webhook auto_verified=%s", verified)

    return {"status": "ok", "verified": verified}
