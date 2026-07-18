"""Parsed listing ready for database upsert."""

from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl, model_validator

from sentinel_suisse.models.enums import EmploymentType, ListingType, PropertyType


class RawListing(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    listing_type: ListingType
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, max_length=200)
    price: Decimal | None = Field(default=None, ge=0)
    rooms: Decimal | None = Field(default=None, ge=0, le=20)
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    job_category: str | None = Field(default=None, min_length=1, max_length=80)
    employment_type: EmploymentType | None = None
    workload_min: int | None = Field(default=None, ge=0, le=100)
    workload_max: int | None = Field(default=None, ge=0, le=100)
    source_url: HttpUrl
    raw_payload: dict | None = None

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
