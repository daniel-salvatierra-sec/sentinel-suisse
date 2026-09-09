"""Parsed listing ready for database upsert."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType, PropertyType


def _normalize_workload_percent(value: Any) -> int | None:
    """Keep Swiss pensum % (0–100). Drop garbage like 360 so one ad cannot abort ingest."""
    if value is None or value == "":
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if number < 0 or number > 100:
        return None
    return number


class RawListing(BaseModel):
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
    is_under_construction: bool | None = None
    job_category: str | None = Field(default=None, min_length=1, max_length=80)
    employment_type: EmploymentType | None = None
    workload_min: int | None = Field(default=None, ge=0, le=100)
    workload_max: int | None = Field(default=None, ge=0, le=100)
    source_url: HttpUrl
    raw_payload: dict | None = None

    @field_validator("workload_min", "workload_max", mode="before")
    @classmethod
    def coerce_workload_percent(cls, value: Any) -> int | None:
        return _normalize_workload_percent(value)

    @model_validator(mode="after")
    def validate_workload_range(self) -> "RawListing":
        if (
            self.workload_min is not None
            and self.workload_max is not None
            and self.workload_min > self.workload_max
        ):
            msg = "workload_min cannot be greater than workload_max"
            raise ValueError(msg)
        return self
