from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

SponsorContext = Literal["all", "housing", "job"]
SponsorPlacement = Literal["banner"]


class SponsorAdCreate(BaseModel):
    sponsor_name: str = Field(min_length=2, max_length=120)
    placement: SponsorPlacement = "banner"
    context: SponsorContext = "all"
    headline: str | None = Field(default=None, max_length=160)
    image_url: HttpUrl | None = None
    target_url: HttpUrl
    monthly_chf: Decimal = Field(default=Decimal("0"), ge=0, le=100000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0, le=9999)

    @model_validator(mode="after")
    def require_creative(self) -> "SponsorAdCreate":
        if not self.headline and not self.image_url:
            msg = "headline or image_url is required"
            raise ValueError(msg)
        if self.starts_at and self.ends_at and self.starts_at > self.ends_at:
            msg = "starts_at cannot be after ends_at"
            raise ValueError(msg)
        return self


class SponsorAdUpdate(BaseModel):
    sponsor_name: str | None = Field(default=None, min_length=2, max_length=120)
    placement: SponsorPlacement | None = None
    context: SponsorContext | None = None
    headline: str | None = Field(default=None, max_length=160)
    image_url: HttpUrl | None = None
    target_url: HttpUrl | None = None
    monthly_chf: Decimal | None = Field(default=None, ge=0, le=100000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0, le=9999)


class SponsorAdAdminRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sponsor_name: str
    placement: str
    context: str
    headline: str | None
    image_url: str | None
    target_url: str
    monthly_chf: Decimal
    starts_at: datetime | None
    ends_at: datetime | None
    is_active: bool
    sort_order: int
    impression_count: int
    click_count: int
    created_at: datetime
    updated_at: datetime


class SponsorAdPublic(BaseModel):
    id: int
    placement: str
    headline: str | None
    image_url: str | None
    target_url: str


class SponsorRevenueSummary(BaseModel):
    active_count: int
    estimated_monthly_chf: Decimal
    total_impressions: int
    total_clicks: int
    active_sponsors: list[SponsorAdAdminRow]


class SponsorEventKind(BaseModel):
    kind: Literal["impression", "click"]

    @field_validator("kind")
    @classmethod
    def normalize_kind(cls, value: str) -> str:
        return value.strip().lower()
