from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from sentinel_suisse.models.enums import ChannelType


class NotificationChannelCreate(BaseModel):
    channel_type: ChannelType
    channel_address: str = Field(min_length=3, max_length=500)
    is_primary: bool = False


class NotificationChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    channel_type: ChannelType
    channel_address: str
    is_verified: bool
    is_primary: bool
    verified_at: datetime | None
    created_at: datetime


class NotificationChannelVerify(BaseModel):
    is_verified: bool = True
