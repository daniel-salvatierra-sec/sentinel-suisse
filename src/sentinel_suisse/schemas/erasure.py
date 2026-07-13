from pydantic import BaseModel


class UserErasureReport(BaseModel):
    """Summary of personal data removed when a user account is erased."""

    user_id: int
    notification_channels_removed: int
    saved_searches_removed: int
    alert_logs_removed: int
