from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, model_validator

from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType, PropertyType


def listing_is_demo(raw_payload: dict | None) -> bool:
    """True for fixture/pilot listings (fake source URLs)."""
    if not isinstance(raw_payload, dict):
        return False
    return raw_payload.get("pilot") is True or raw_payload.get("source") == "fixture"


class ListingCreate(BaseModel):
    provider_id: int = Field(gt=0)
    external_id: str = Field(min_length=1, max_length=255)
    listing_type: ListingType
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, max_length=200)
    country: CountryCode = CountryCode.CH
    price: Decimal | None = Field(default=None, ge=0)
    rooms: Decimal | None = Field(default=None, ge=0, le=20)
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    job_category: str | None = Field(default=None, min_length=1, max_length=80)
    employment_type: EmploymentType | None = None
    workload_min: int | None = Field(default=None, ge=0, le=100)
    workload_max: int | None = Field(default=None, ge=0, le=100)
    source_url: HttpUrl
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    fetched_at: datetime

    @model_validator(mode="after")
    def validate_workload_range(self) -> "ListingCreate":
        if (
            self.workload_min is not None
            and self.workload_max is not None
            and self.workload_min > self.workload_max
        ):
            msg = "workload_min cannot be greater than workload_max"
            raise ValueError(msg)
        return self


class ListingUpdate(BaseModel):
    external_id: str | None = Field(default=None, min_length=1, max_length=255)
    listing_type: ListingType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, max_length=200)
    country: CountryCode | None = None
    price: Decimal | None = Field(default=None, ge=0)
    rooms: Decimal | None = Field(default=None, ge=0, le=20)
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    job_category: str | None = Field(default=None, min_length=1, max_length=80)
    employment_type: EmploymentType | None = None
    workload_min: int | None = Field(default=None, ge=0, le=100)
    workload_max: int | None = Field(default=None, ge=0, le=100)
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
    country: CountryCode = CountryCode.CH
    price: Decimal | None
    rooms: Decimal | None = None
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    job_category: str | None = None
    employment_type: EmploymentType | None = None
    workload_min: int | None = None
    workload_max: int | None = None
    source_url: str
    content_hash: str
    fetched_at: datetime
    # Loaded from ORM for is_demo; never exposed in JSON.
    raw_payload: dict | None = Field(default=None, exclude=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_demo(self) -> bool:
        return listing_is_demo(self.raw_payload)
