"""Right-to-erasure (nLPD / GDPR) — delete user and cascaded personal data."""

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.alert_log import AlertLog
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.models.user import User


@dataclass
class ErasureResult:
    user_id: int
    notification_channels_removed: int
    saved_searches_removed: int
    alert_logs_removed: int


def erase_user(db: Session, user: User) -> ErasureResult:
    """Delete user row; DB CASCADE removes channels, searches, and alert logs."""
    user_id = user.id
    channels_removed = db.scalar(
        select(func.count())
        .select_from(NotificationChannel)
        .where(NotificationChannel.user_id == user_id)
    )
    searches_removed = db.scalar(
        select(func.count()).select_from(SavedSearch).where(SavedSearch.user_id == user_id)
    )
    alerts_removed = db.scalar(
        select(func.count()).select_from(AlertLog).where(AlertLog.user_id == user_id)
    )

    db.delete(user)
    db.commit()

    return ErasureResult(
        user_id=user_id,
        notification_channels_removed=channels_removed or 0,
        saved_searches_removed=searches_removed or 0,
        alert_logs_removed=alerts_removed or 0,
    )
