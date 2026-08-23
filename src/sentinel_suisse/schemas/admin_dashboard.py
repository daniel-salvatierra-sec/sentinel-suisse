from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from sentinel_suisse.models.enums import ListingType


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


class ListingVisibilityUpdate(BaseModel):
    is_hidden: bool


class UserPremiumUpdate(BaseModel):
    is_premium: bool


class AdminUserRow(BaseModel):
    id: int
    email: str
    locale: str
    is_active: bool
    is_premium: bool
    created_at: datetime
    saved_search_count: int = Field(default=0)
