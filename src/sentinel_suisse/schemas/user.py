from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from sentinel_suisse.config import get_settings
from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.models.user import User
from sentinel_suisse.security.pii import decrypt_pii
from sentinel_suisse.services.entitlements import can_receive_alerts, max_saved_searches

UserLocale = Literal["fr", "de", "es", "pt", "en"]
AcceptGoal = Literal["housing", "job", "both"]
AcceptPermit = Literal["G", "B", "C", "L", "none", "other"]

_SHORT = 80


def _clip(value: str) -> str:
    return value.strip()[:_SHORT]


class AcceptProfile(BaseModel):
    """Voluntary constraints. Matching is honest reasons, never a magic score."""

    goal: AcceptGoal | None = None
    live_in: str = ""
    work_in: str = ""
    permit: AcceptPermit | None = None
    languages: str = ""
    budget_chf: int | None = Field(default=None, ge=1, le=20_000)
    cities: str = ""
    move_in: str = ""
    household: int | None = Field(default=None, ge=1, le=12)

    @field_validator("live_in", "work_in", "languages", "cities", "move_in", mode="before")
    @classmethod
    def _clip_text(cls, value: object) -> str:
        if value is None:
            return ""
        return _clip(str(value))


class UserCreate(BaseModel):
    email: EmailStr
    is_active: bool = True
    locale: UserLocale = DEFAULT_LANGUAGE
    is_premium: bool = False


class UserRead(BaseModel):
    id: int
    email: str
    locale: UserLocale
    is_active: bool
    is_premium: bool = False
    free_alerts_grandfathered: bool = False
    can_receive_alerts: bool = False
    saved_search_limit: int
    saved_search_count: int = 0
    accept_profile: AcceptProfile | None = None
    created_at: datetime


def parse_accept_profile(raw: object) -> AcceptProfile | None:
    if not raw or not isinstance(raw, dict):
        return None
    try:
        parsed = AcceptProfile.model_validate(raw)
    except ValueError:
        return None
    dumped = parsed.model_dump()
    if not any(
        dumped[key]
        for key in (
            "goal",
            "live_in",
            "work_in",
            "permit",
            "languages",
            "budget_chf",
            "cities",
            "move_in",
            "household",
        )
    ):
        return None
    return parsed


def to_user_read(user: User, *, saved_search_count: int = 0) -> UserRead:
    return UserRead(
        id=user.id,
        email=decrypt_pii(user.email),
        locale=user.locale,  # type: ignore[arg-type]
        is_active=user.is_active,
        is_premium=user.is_premium,
        free_alerts_grandfathered=user.free_alerts_grandfathered,
        can_receive_alerts=can_receive_alerts(user),
        saved_search_limit=max_saved_searches(user, get_settings()),
        saved_search_count=saved_search_count,
        accept_profile=parse_accept_profile(user.accept_profile),
        created_at=user.created_at,
    )


class UserCreated(UserRead):
    """Returned once on user creation — api_key is not stored in plaintext."""

    api_key: str = Field(min_length=32)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    locale: UserLocale | None = None
    is_active: bool | None = None
    is_premium: bool | None = None


class UserAcceptProfileUpdate(BaseModel):
    accept_profile: AcceptProfile
