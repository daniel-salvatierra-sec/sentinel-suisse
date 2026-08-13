"""Optional AI assistant (free-form chat) routes. Public — no auth required."""

from fastapi import APIRouter, HTTPException, Request, status

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantConfig,
)
from sentinel_suisse.services.assistant import AssistantError, ask_assistant

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.get("/config", response_model=AssistantConfig)
@limiter.limit(lambda: get_settings().rate_limit)
def assistant_config(request: Request) -> AssistantConfig:
    """Public: whether the AI assistant is configured (no auth)."""
    settings = get_settings()
    return AssistantConfig(
        enabled=settings.assistant_is_enabled(),
        max_input_chars=settings.assistant_max_input_chars,
    )


@router.post("/chat", response_model=AssistantChatResponse)
@limiter.limit(lambda: get_settings().assistant_rate_limit)
def assistant_chat(request: Request, payload: AssistantChatRequest) -> AssistantChatResponse:
    """Send a free-form message to the AI assistant. Rate limited to bound API cost."""
    settings = get_settings()
    if not settings.assistant_is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="assistant_disabled",
        )

    message = payload.message.strip()[: settings.assistant_max_input_chars]
    if not message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty_message")

    history = [{"role": item.role, "content": item.content} for item in payload.history]

    try:
        reply = ask_assistant(message, payload.lang, history, settings)
    except AssistantError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.code,
        ) from exc

    return AssistantChatResponse(reply=reply)
