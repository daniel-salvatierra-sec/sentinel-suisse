"""Listing search query builder."""

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.job_taxonomy import (
    BRANCH_PARENT,
    non_other_stored_values,
    stored_job_category_values,
)
from sentinel_suisse.services.listing_freshness import apply_freshness_filter
from sentinel_suisse.services.location_match import expand_location_query


def search_listings(
    db: Session,
    filters: SearchQuery,
    *,
    limit: int,
    offset: int,
) -> list[Listing]:
    stmt = _apply_filters(select(Listing), filters)
    stmt = apply_freshness_filter(stmt)
    stmt = stmt.order_by(Listing.fetched_at.desc(), Listing.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def _apply_filters(stmt: Select[tuple[Listing]], filters: SearchQuery) -> Select[tuple[Listing]]:
    if filters.listing_type is not None:
        stmt = stmt.where(Listing.listing_type == filters.listing_type)
    if filters.location is not None:
        terms = expand_location_query(filters.location)
        if terms:
            stmt = stmt.where(or_(*[Listing.location.ilike(f"%{term}%") for term in terms]))
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
    if filters.is_under_construction is True:
        stmt = stmt.where(Listing.is_under_construction.is_(True))
    elif filters.is_under_construction is False:
        stmt = stmt.where(
            or_(
                Listing.is_under_construction.is_(None),
                Listing.is_under_construction.is_(False),
            )
        )
    if filters.job_category is not None:
        stmt = _apply_job_category_filter(stmt, filters.job_category)
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


def _apply_job_category_filter(
    stmt: Select[tuple[Listing]], filter_category: str
) -> Select[tuple[Listing]]:
    values = [item.casefold() for item in stored_job_category_values(filter_category)]
    parent = BRANCH_PARENT.get(filter_category, filter_category)
    if parent == "other" or filter_category == "other":
        excluded = [item.casefold() for item in non_other_stored_values()]
        return stmt.where(
            or_(
                Listing.job_category.is_(None),
                func.lower(Listing.job_category).in_(values),
                ~func.lower(Listing.job_category).in_(excluded),
            )
        )
    return stmt.where(func.lower(Listing.job_category).in_(values))
