"""Payload for a user-posted housing or job listing."""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType, PropertyType
from sentinel_suisse.services.contact_link import ContactLinkError, normalize_contact_link
from sentinel_suisse.services.job_taxonomy import canonical_job_category


class DirectListingCreate(BaseModel):
    listing_type: ListingType = ListingType.HOUSING
    title: str = Field(min_length=8, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str = Field(min_length=2, max_length=200)
    country: CountryCode = CountryCode.CH
    contact_url: str = Field(min_length=6, max_length=1000)
    price: Decimal | None = Field(default=None, ge=1, le=200000)
    rooms: Decimal | None = Field(default=None, ge=0, le=20)
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    job_category: str | None = Field(default=None, min_length=1, max_length=80)
    employment_type: EmploymentType | None = None
    workload_min: int | None = Field(default=None, ge=0, le=100)
    workload_max: int | None = Field(default=None, ge=0, le=100)

    @field_validator("contact_url")
    @classmethod
    def normalize_contact(cls, value: str) -> str:
        try:
            return normalize_contact_link(value)
        except ContactLinkError as exc:
            raise ValueError(str(exc)) from exc

    @model_validator(mode="after")
    def validate_by_type(self) -> "DirectListingCreate":
        if self.listing_type == ListingType.HOUSING and self.price is None:
            msg = "price is required for housing"
            raise ValueError(msg)
        if self.listing_type == ListingType.JOB:
            self.job_category = canonical_job_category(self.job_category) or "other"
        return self
