"""Parsed listing ready for database upsert."""

from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl

from sentinel_suisse.models.enums import ListingType


class RawListing(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    listing_type: ListingType
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, max_length=200)
    price: Decimal | None = Field(default=None, ge=0)
    source_url: HttpUrl
    raw_payload: dict | None = None
