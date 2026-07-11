from datetime import datetime

from pydantic import BaseModel, Field

from sentinel_suisse.models.enums import ChannelType
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.security.pii import decrypt_pii


class NotificationChannelCreate(BaseModel):
    channel_type: ChannelType
    channel_address: str = Field(min_length=3, max_length=500)
    is_primary: bool = False


class NotificationChannelRead(BaseModel):
    id: int
    user_id: int
    channel_type: ChannelType
    channel_address: str
    is_verified: bool
    is_primary: bool
    verified_at: datetime | None
    created_at: datetime


def to_channel_read(channel: NotificationChannel) -> NotificationChannelRead:
    return NotificationChannelRead(
        id=channel.id,
        user_id=channel.user_id,
        channel_type=channel.channel_type,
        channel_address=decrypt_pii(channel.channel_address),
        is_verified=channel.is_verified,
        is_primary=channel.is_primary,
        verified_at=channel.verified_at,
        created_at=channel.created_at,
    )


class NotificationChannelVerify(BaseModel):
    is_verified: bool = True
