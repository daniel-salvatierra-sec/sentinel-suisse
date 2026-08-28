"""Authenticated sponsor ad self-serve routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.sponsor_ad import SponsorAdOwnerRow
from sentinel_suisse.services.sponsor_ads import list_user_sponsors

router = APIRouter(prefix="/me/sponsors", tags=["sponsors"])


@router.get("", response_model=list[SponsorAdOwnerRow])
@limiter.limit(lambda: get_settings().rate_limit)
def get_my_sponsors(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SponsorAdOwnerRow]:
    return list_user_sponsors(db, current_user.id)
