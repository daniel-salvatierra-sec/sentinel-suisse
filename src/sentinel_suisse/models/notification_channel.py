from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_suisse.db.base import Base
from sentinel_suisse.models.enums import ChannelType

if TYPE_CHECKING:
    from sentinel_suisse.models.user import User


class NotificationChannel(Base):
    """User notification preference (WhatsApp, email, etc.)."""

    __tablename__ = "notification_channels"
    __table_args__ = (UniqueConstraint("user_id", "channel_type", name="uq_user_channel_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel_type: Mapped[ChannelType] = mapped_column(nullable=False)
    # PII: encrypt at rest before production — phone/email/tokenized address
    channel_address: Mapped[str] = mapped_column(String(500), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="notification_channels")
