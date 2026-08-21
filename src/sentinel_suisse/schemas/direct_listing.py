"""Payload for a user-posted housing listing."""

from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl

from sentinel_suisse.models.enums import CountryCode, PropertyType


class DirectListingCreate(BaseModel):
    title: str = Field(min_length=8, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str = Field(min_length=2, max_length=200)
    country: CountryCode = CountryCode.CH
    price: Decimal = Field(ge=1, le=50000)
    rooms: Decimal | None = Field(default=None, ge=0, le=20)
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    contact_url: HttpUrl
