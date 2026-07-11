"""User notification channel routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user, verify_admin
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.notification_channel import (
    NotificationChannelCreate,
    NotificationChannelRead,
    NotificationChannelVerify,
)

router = APIRouter(prefix="/notification-channels", tags=["notification-channels"])


@router.get("", response_model=list[NotificationChannelRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_channels(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationChannel]:
    stmt = (
        select(NotificationChannel)
        .where(NotificationChannel.user_id == current_user.id)
        .order_by(NotificationChannel.id)
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=NotificationChannelRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def create_channel(
    request: Request,
    payload: NotificationChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationChannel:
    channel = NotificationChannel(
        user_id=current_user.id,
        channel_type=payload.channel_type,
        channel_address=payload.channel_address,
        is_verified=False,
        is_primary=payload.is_primary,
        created_at=datetime.now(UTC),
    )
    db.add(channel)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Channel type already registered for this user",
        ) from exc
    db.refresh(channel)
    return channel


@router.patch("/{channel_id}/verify", response_model=NotificationChannelRead)
@limiter.limit(lambda: get_settings().rate_limit)
def verify_channel(
    request: Request,
    channel_id: int,
    payload: NotificationChannelVerify,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> NotificationChannel:
    channel = db.get(NotificationChannel, channel_id)
    if channel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    channel.is_verified = payload.is_verified
    channel.verified_at = datetime.now(UTC) if payload.is_verified else None
    db.commit()
    db.refresh(channel)
    return channel
