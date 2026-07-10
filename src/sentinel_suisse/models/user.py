from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_suisse.db.base import Base

if TYPE_CHECKING:
    from sentinel_suisse.models.notification_channel import NotificationChannel
    from sentinel_suisse.models.saved_search import SavedSearch


class User(Base):
    """Application user (alert subscriber)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # PII: encrypt at rest before production (nLPD) — see docs/privacy/data-map.md
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    notification_channels: Mapped[list["NotificationChannel"]] = relationship(back_populates="user")
    saved_searches: Mapped[list["SavedSearch"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id}>"
