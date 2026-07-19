"""Listing search query builder."""

from sqlalchemy import Select, and_, or_, select
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
    if filters.country is not None:
        stmt = stmt.where(Listing.country == filters.country)
    if filters.price_min is not None:
        stmt = stmt.where(Listing.price >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(Listing.price <= filters.price_max)
    if filters.rooms_min is not None:
        stmt = stmt.where(or_(Listing.rooms.is_(None), Listing.rooms >= filters.rooms_min))
    if filters.property_type is not None:
        stmt = stmt.where(
            or_(Listing.property_type.is_(None), Listing.property_type == filters.property_type)
        )
    if filters.has_parking is True:
        stmt = stmt.where(or_(Listing.has_parking.is_(None), Listing.has_parking.is_(True)))
    elif filters.has_parking is False:
        stmt = stmt.where(or_(Listing.has_parking.is_(None), Listing.has_parking.is_(False)))
    if filters.job_category is not None:
        stmt = stmt.where(
            or_(
                Listing.job_category.is_(None),
                Listing.job_category == filters.job_category,
            )
        )
    if filters.employment_type is not None:
        stmt = stmt.where(
            or_(
                Listing.employment_type.is_(None),
                Listing.employment_type == filters.employment_type,
            )
        )
    if filters.workload_min is not None or filters.workload_max is not None:
        filter_min = filters.workload_min if filters.workload_min is not None else 0
        filter_max = filters.workload_max if filters.workload_max is not None else 100
        # Overlap when listing range is known; include unknown (NULL) listings.
        stmt = stmt.where(
            or_(
                and_(Listing.workload_min.is_(None), Listing.workload_max.is_(None)),
                and_(
                    or_(Listing.workload_max.is_(None), Listing.workload_max >= filter_min),
                    or_(Listing.workload_min.is_(None), Listing.workload_min <= filter_max),
                ),
            )
        )
    provider_ids = filters.resolved_provider_ids()
    if provider_ids is not None:
        stmt = stmt.where(Listing.provider_id.in_(provider_ids))
    return stmt
