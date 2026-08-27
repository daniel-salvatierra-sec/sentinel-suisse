"""Public city picker stock (housing + jobs)."""

from pydantic import BaseModel, Field


class CityStock(BaseModel):
    city: str
    housing_count: int = Field(ge=0)
    job_count: int = Field(ge=0)
    total: int = Field(ge=0)
