from datetime import datetime

from pydantic import BaseModel, ConfigDict

from sentinel_suisse.models.enums import AlertStatus


class DispatchStatsRead(BaseModel):
    matched: int
    sent: int
    skipped: int
    failed: int


class AlertLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    saved_search_id: int
    listing_id: int
    channel_type: str
    status: AlertStatus
    error_message: str | None
    sent_at: datetime | None
    created_at: datetime
