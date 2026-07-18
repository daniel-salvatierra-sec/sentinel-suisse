from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_suisse.db.base import Base
from sentinel_suisse.models.enums import EmploymentType, ListingType, PropertyType, enum_values

if TYPE_CHECKING:
    from sentinel_suisse.models.provider import Provider


class Listing(Base):
    """Aggregated listing from an external provider."""

    __tablename__ = "listings"
    __table_args__ = (
        UniqueConstraint("provider_id", "external_id", name="uq_listing_provider_external"),
        Index("ix_listings_listing_type", "listing_type"),
        Index("ix_listings_content_hash", "content_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id", ondelete="RESTRICT"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    listing_type: Mapped[ListingType] = mapped_column(
        Enum(
            ListingType,
            name="listing_type",
            create_type=False,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    rooms: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    property_type: Mapped[PropertyType | None] = mapped_column(
        Enum(
            PropertyType,
            name="property_type",
            create_type=False,
            values_callable=enum_values,
        ),
        nullable=True,
    )
    has_parking: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    job_category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(
            EmploymentType,
            name="employment_type",
            create_type=False,
            values_callable=enum_values,
        ),
        nullable=True,
    )
    workload_min: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    workload_max: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    provider: Mapped["Provider"] = relationship(back_populates="listings")

    def __repr__(self) -> str:
        return f"<Listing provider_id={self.provider_id} external_id={self.external_id!r}>"
