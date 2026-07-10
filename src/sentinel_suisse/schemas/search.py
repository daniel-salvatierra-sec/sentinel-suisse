from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from sentinel_suisse.models.enums import ListingType


class SearchQuery(BaseModel):
    """Validated search filters — stored in saved_searches.query and used by /search."""

    listing_type: ListingType | None = None
    location: str | None = Field(default=None, min_length=1, max_length=200)
    price_min: Decimal | None = Field(default=None, ge=0)
    price_max: Decimal | None = Field(default=None, ge=0)
    provider_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_price_range(self) -> "SearchQuery":
        if (
            self.price_min is not None
            and self.price_max is not None
            and self.price_min > self.price_max
        ):
            msg = "price_min cannot be greater than price_max"
            raise ValueError(msg)
        return self
