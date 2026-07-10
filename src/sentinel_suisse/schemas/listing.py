from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from sentinel_suisse.models.enums import ListingType


class ListingCreate(BaseModel):
    provider_id: int = Field(gt=0)
    external_id: str = Field(min_length=1, max_length=255)
    listing_type: ListingType
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, max_length=200)
    price: Decimal | None = Field(default=None, ge=0)
    source_url: HttpUrl
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    fetched_at: datetime


class ListingUpdate(BaseModel):
    external_id: str | None = Field(default=None, min_length=1, max_length=255)
    listing_type: ListingType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, max_length=200)
    price: Decimal | None = Field(default=None, ge=0)
    source_url: HttpUrl | None = None
    content_hash: str | None = Field(
        default=None, min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$"
    )
    fetched_at: datetime | None = None


class ListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    external_id: str
    listing_type: ListingType
    title: str
    description: str | None
    location: str | None
    price: Decimal | None
    source_url: str
    content_hash: str
    fetched_at: datetime
