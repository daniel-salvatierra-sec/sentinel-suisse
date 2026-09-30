"""Listing search query builder."""

from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import Select, and_, case, func, not_, nulls_last, or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.enums import CountryCode
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.housing_construction import construction_match_clause
from sentinel_suisse.services.job_taxonomy import (
    non_other_stored_values,
    parent_field,
    stored_job_category_values,
    title_needles_for_filter,
)
from sentinel_suisse.services.listing_freshness import apply_freshness_filter, listing_is_fresh
from sentinel_suisse.services.location_match import (
    expand_location_query,
    is_border_place,
    neighbor_belt_terms,
    resolve_search_location,
)
from sentinel_suisse.services.search_terms import (
    expand_text_query,
    is_occupation_query,
    occupation_category,
    occupation_title_rejects,
    query_looks_like_job,
)

SearchSort = Literal["newest", "price_asc", "price_desc"]


def _featured_rank():
    now = datetime.now(UTC)
    return case(
        (
            and_(
                Listing.is_featured.is_(True),
                or_(Listing.featured_until.is_(None), Listing.featured_until > now),
            ),
            1,
        ),
        else_=0,
    )


def search_listings(
    db: Session,
    filters: SearchQuery,
    *,
    limit: int,
    offset: int,
    sort: SearchSort = "newest",
) -> list[Listing]:
    stmt = _apply_filters(select(Listing), filters)
    stmt = apply_freshness_filter(stmt)
    stmt = _apply_sort(stmt, sort, filters).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def _occupation_text(filters: SearchQuery) -> str | None:
    keyword = (filters.keyword or "").strip()
    if keyword and is_occupation_query(keyword):
        return keyword
    location = (filters.location or "").strip()
    if location and is_occupation_query(location):
        return location
    return None


def _driver_section_rank():
    """Bus, truck, taxi, delivery, then other driver titles."""
    sections = (
        ("%bus%", "%trolley%", "%tram%", "%postauto%", "%autobus%", "%autocar%"),
        ("%lkw%", "%poids lourd%", "%camion%", "%sattel%", "%anhänger%", "%anhaenger%"),
        ("%taxi%", "%vtc%"),
        ("%livreur%", "%liefer%", "%zustell%", "%coursier%", "%kurier%"),
    )
    whens = [
        (or_(*(Listing.title.ilike(needle) for needle in needles)), index)
        for index, needles in enumerate(sections)
    ]
    return case(*whens, else_=len(sections))


def _apply_sort(
    stmt: Select[tuple[Listing]],
    sort: SearchSort,
    filters: SearchQuery | None = None,
) -> Select[tuple[Listing]]:
    featured = _featured_rank().desc()
    if sort == "price_asc":
        return stmt.order_by(featured, nulls_last(Listing.price.asc()), Listing.id.desc())
    if sort == "price_desc":
        return stmt.order_by(featured, nulls_last(Listing.price.desc()), Listing.id.desc())
    text = _occupation_text(filters) if filters is not None else None
    if text and occupation_category(text) == "transport":
        return stmt.order_by(
            featured,
            _driver_section_rank().asc(),
            Listing.fetched_at.desc(),
            Listing.id.desc(),
        )
    return stmt.order_by(featured, Listing.fetched_at.desc(), Listing.id.desc())


def get_public_listing(db: Session, listing_id: int) -> Listing | None:
    listing = db.get(Listing, listing_id)
    if listing is None or listing.is_hidden:
        return None
    if not listing_is_fresh(listing):
        return None
    return listing


def _apply_filters(stmt: Select[tuple[Listing]], filters: SearchQuery) -> Select[tuple[Listing]]:
    stmt = stmt.where(Listing.is_hidden.is_(False))
    if filters.listing_type is not None:
        stmt = stmt.where(Listing.listing_type == filters.listing_type)
    location = resolve_search_location(
        filters.country.value if filters.country is not None else None,
        filters.location,
    )
    keyword = (filters.keyword or "").strip()
    occupation = _occupation_text(filters)
    # A bare occupation in `location` is the job word, not a city.
    place = None if occupation and is_occupation_query(location or "") and not keyword else location
    if place is not None:
        terms = expand_location_query(place)
        clauses = [Listing.location.ilike(f"%{term}%") for term in terms]
        # Occupation words typed with a city ("fleuriste Genève") still scan titles.
        # City names must not: ILIKE %sion% matches "pension" / "décision".
        if query_looks_like_job(place) and not is_occupation_query(place):
            for needle in expand_text_query(place):
                clauses.append(Listing.title.ilike(f"%{needle}%"))
        if clauses:
            stmt = stmt.where(or_(*clauses))
    if keyword and not is_occupation_query(keyword):
        stmt = stmt.where(
            or_(
                Listing.location.ilike(f"%{keyword}%"),
                Listing.title.ilike(f"%{keyword}%"),
            )
        )
    if occupation is not None:
        title_hits = [
            Listing.title.ilike(f"%{needle}%") for needle in expand_text_query(occupation)
        ]
        if title_hits:
            stmt = stmt.where(or_(*title_hits))
        for reject in occupation_title_rejects(occupation):
            stmt = stmt.where(~Listing.title.ilike(f"%{reject}%"))
    if filters.country is not None and not is_border_place(location):
        stmt = stmt.where(Listing.country == filters.country)
    if filters.country == CountryCode.CH:
        belt = [Listing.location.ilike(f"%{term}%") for term in neighbor_belt_terms()]
        if belt:
            stmt = stmt.where(not_(or_(*belt)))
    if filters.price_min is not None:
        stmt = stmt.where(Listing.price >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(Listing.price <= filters.price_max)
    if filters.rooms_min is not None:
        stmt = stmt.where(Listing.rooms >= filters.rooms_min)
    if filters.property_type is not None:
        stmt = stmt.where(Listing.property_type == filters.property_type)
    if filters.has_parking is True:
        stmt = stmt.where(or_(Listing.has_parking.is_(None), Listing.has_parking.is_(True)))
    elif filters.has_parking is False:
        stmt = stmt.where(or_(Listing.has_parking.is_(None), Listing.has_parking.is_(False)))
    if filters.is_under_construction is True:
        stmt = stmt.where(construction_match_clause())
    elif filters.is_under_construction is False:
        stmt = stmt.where(not_(construction_match_clause()))
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
    values = [
        item.casefold() for item in stored_job_category_values(filter_category, for_search=True)
    ]
    clauses = [func.lower(Listing.job_category).in_(values)]
    for needle in title_needles_for_filter(filter_category, for_search=True):
        clauses.append(Listing.title.ilike(needle))
    parent = parent_field(filter_category)
    if parent == "other" or filter_category == "other":
        excluded = [item.casefold() for item in non_other_stored_values()]
        clauses.extend(
            [
                Listing.job_category.is_(None),
                func.lower(Listing.job_category) == "unknown",
                ~func.lower(Listing.job_category).in_(excluded),
            ]
        )
    return stmt.where(or_(*clauses))
