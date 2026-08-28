from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_suisse.db.base import Base


class SponsorAd(Base):
    """Manual sponsor placement (Phase 1 — operator-managed, no ad network)."""

    __tablename__ = "sponsor_ads"
    __table_args__ = (
        Index("ix_sponsor_ads_active", "is_active", "starts_at", "ends_at"),
        Index("ix_sponsor_ads_context", "context"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sponsor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    placement: Mapped[str] = mapped_column(String(32), nullable=False, default="banner")
    context: Mapped[str] = mapped_column(String(16), nullable=False, default="all")
    headline: Mapped[str | None] = mapped_column(String(160), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    target_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    monthly_chf: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    impression_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    click_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    stripe_checkout_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
