from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_suisse.db.base import Base

if TYPE_CHECKING:
    from sentinel_suisse.models.listing import Listing


class Provider(Base):
    """External listing source (e.g. job portal, housing portal)."""

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    listings: Mapped[list["Listing"]] = relationship(back_populates="provider")

    def __repr__(self) -> str:
        return f"<Provider slug={self.slug!r}>"
