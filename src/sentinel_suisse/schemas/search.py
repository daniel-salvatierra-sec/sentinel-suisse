from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType, PropertyType


class SearchQuery(BaseModel):
    """Validated search filters — stored in saved_searches.query and used by /search."""

    listing_type: ListingType | None = None
    location: str | None = Field(default=None, min_length=1, max_length=200)
    country: CountryCode | None = None
    price_min: Decimal | None = Field(default=None, ge=0)
    price_max: Decimal | None = Field(default=None, ge=0)
    rooms_min: Decimal | None = Field(default=None, ge=0, le=20)
    property_type: PropertyType | None = None
    has_parking: bool | None = None
    job_category: str | None = Field(default=None, min_length=1, max_length=80)
    employment_type: EmploymentType | None = None
    workload_min: int | None = Field(default=None, ge=0, le=100)
    workload_max: int | None = Field(default=None, ge=0, le=100)
    provider_id: int | None = Field(default=None, gt=0)
    provider_ids: list[int] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_ranges(self) -> "SearchQuery":
        if (
            self.price_min is not None
            and self.price_max is not None
            and self.price_min > self.price_max
        ):
            msg = "price_min cannot be greater than price_max"
            raise ValueError(msg)
        if (
            self.workload_min is not None
            and self.workload_max is not None
            and self.workload_min > self.workload_max
        ):
            msg = "workload_min cannot be greater than workload_max"
            raise ValueError(msg)
        return self

    def resolved_provider_ids(self) -> list[int] | None:
        ids: set[int] = set()
        if self.provider_ids:
            ids.update(pid for pid in self.provider_ids if pid > 0)
        if self.provider_id is not None:
            ids.add(self.provider_id)
        return sorted(ids) if ids else None
