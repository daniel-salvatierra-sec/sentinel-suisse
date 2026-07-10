"""Listing search query builder."""

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery


def search_listings(
    db: Session,
    filters: SearchQuery,
    *,
    limit: int,
    offset: int,
) -> list[Listing]:
    stmt = _apply_filters(select(Listing), filters)
    stmt = stmt.order_by(Listing.fetched_at.desc(), Listing.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def _apply_filters(stmt: Select[tuple[Listing]], filters: SearchQuery) -> Select[tuple[Listing]]:
    if filters.listing_type is not None:
        stmt = stmt.where(Listing.listing_type == filters.listing_type)
    if filters.location is not None:
        stmt = stmt.where(Listing.location.ilike(f"%{filters.location}%"))
    if filters.price_min is not None:
        stmt = stmt.where(Listing.price >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(Listing.price <= filters.price_max)
    if filters.provider_id is not None:
        stmt = stmt.where(Listing.provider_id == filters.provider_id)
    return stmt
