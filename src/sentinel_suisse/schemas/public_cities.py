"""Public city picker stock (housing + jobs)."""

from pydantic import BaseModel, Field

from sentinel_suisse.models.enums import CountryCode


class CityStock(BaseModel):
    city: str
    country: CountryCode
    housing_count: int = Field(ge=0)
    job_count: int = Field(ge=0)
    total: int = Field(ge=0)
