from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.schemas.direct_listing import DirectListingCreate
from sentinel_suisse.services.contact_link import ContactLinkError, normalize_contact_link


class ProviderIngestHealth(BaseModel):
    slug: str
    name: str
    is_active: bool
    listing_count: int
    last_fetched_at: datetime | None
    hours_since_fetch: float | None
    stale: bool


class DashboardOverview(BaseModel):
    users_total: int
    users_active: int
    users_premium: int
    listings_housing: int
    listings_job: int
    listings_direct: int
    listings_hidden: int
    listing_fresh_hours: int
    database_ok: bool
    providers: list[ProviderIngestHealth]


class AdminListingRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    listing_type: ListingType
    location: str | None
    source_url: str
    fetched_at: datetime
    is_hidden: bool
    owner_user_id: int | None
    provider_slug: str
    description: str | None = None
    price: Decimal | None = None


class ListingVisibilityUpdate(BaseModel):
    is_hidden: bool


class UserPremiumUpdate(BaseModel):
    is_premium: bool


class UserFreeAlertsUpdate(BaseModel):
    free_alerts_grandfathered: bool


class AdminListingCreate(DirectListingCreate):
    owner_user_id: int | None = None
    is_hidden: bool = False


class AdminListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=8, max_length=300)
    description: str | None = Field(default=None, max_length=10000)
    location: str | None = Field(default=None, min_length=2, max_length=200)
    contact_url: str | None = Field(default=None, min_length=6, max_length=1000)
    price: Decimal | None = Field(default=None, ge=1, le=200000)
    listing_type: ListingType | None = None
    is_hidden: bool | None = None

    @field_validator("contact_url")
    @classmethod
    def normalize_contact(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return normalize_contact_link(value)
        except ContactLinkError as exc:
            raise ValueError(str(exc)) from exc


class AdminUserRow(BaseModel):
    id: int
    email: str
    locale: str
    is_active: bool
    is_premium: bool
    created_at: datetime
    saved_search_count: int = Field(default=0)
