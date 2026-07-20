"""Freemium entitlements (stub — no payments)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.models.user import User


class EntitlementError(Exception):
    """Raised when a freemium limit blocks an action."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def max_saved_searches(user: User, settings: Settings | None = None) -> int:
    cfg = settings or get_settings()
    if user.is_premium:
        return cfg.premium_max_saved_searches
    return cfg.free_max_saved_searches


def count_saved_searches(db: Session, user: User) -> int:
    return int(
        db.scalar(
            select(func.count()).select_from(SavedSearch).where(SavedSearch.user_id == user.id)
        )
        or 0
    )


def assert_can_create_saved_search(
    db: Session,
    user: User,
    settings: Settings | None = None,
) -> None:
    cfg = settings or get_settings()
    limit = max_saved_searches(user, cfg)
    if count_saved_searches(db, user) >= limit:
        raise EntitlementError(
            "saved_search_limit",
            f"Saved search limit reached ({limit}). Upgrade to Premium for more alerts.",
        )


def assert_can_use_whatsapp(user: User) -> None:
    if not user.is_premium:
        raise EntitlementError(
            "whatsapp_requires_premium",
            "WhatsApp alerts require Premium.",
        )
