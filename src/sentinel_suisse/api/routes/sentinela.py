"""Sentinela turn — public, works without an LLM key."""

from fastapi import APIRouter, HTTPException, Request, status

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.schemas.sentinela import SentinelaTurnRequest, SentinelaTurnResponse
from sentinel_suisse.services.sentinela_turn import plan_turn

router = APIRouter(prefix="/sentinela", tags=["sentinela"])


@router.post("/turn", response_model=SentinelaTurnResponse)
@limiter.limit(lambda: get_settings().rate_limit)
def sentinela_turn(request: Request, payload: SentinelaTurnRequest) -> SentinelaTurnResponse:
    """Parse a user sentence into UI actions. Regex fallback; no paywall."""
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty_message")
    payload.message = message[: get_settings().assistant_max_input_chars]
    return plan_turn(payload)
