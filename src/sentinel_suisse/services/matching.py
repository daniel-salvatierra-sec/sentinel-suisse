"""Match listings against saved search filters."""

from sentinel_suisse.models.enums import CountryCode
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.housing_construction import listing_looks_under_construction
from sentinel_suisse.services.job_taxonomy import job_category_matches
from sentinel_suisse.services.listing_freshness import listing_is_fresh
from sentinel_suisse.services.location_match import (
    is_border_place,
    location_in_neighbor_belt,
    location_matches,
    resolve_search_location,
)
from sentinel_suisse.services.search_terms import (
    _fold,
    is_occupation_query,
    occupation_tokens,
    required_extra_terms,
    title_matches_job_query,
)


def _fold_listing_text(title: str | None, location: str | None) -> str:
    return _fold(f"{title or ''} {location or ''}")


def listing_matches_query(listing: Listing, filters: SearchQuery) -> bool:
    if not listing_is_fresh(listing):
        return False
    if listing.is_hidden:
        return False
    if filters.listing_type is not None and listing.listing_type != filters.listing_type:
        return False
    location = resolve_search_location(
        filters.country.value if filters.country is not None else None,
        filters.location,
    )
    keyword = (filters.keyword or "").strip()
    occupation = keyword if keyword and is_occupation_query(keyword) else None
    if occupation is None and location and is_occupation_query(location):
        occupation = location
    place = location
    if occupation and location and is_occupation_query(location) and not keyword:
        place = None
    if place is not None and not occupation_tokens(place):
        if not location_matches(listing.location, place):
            return False
    role_text = " ".join(part for part in (keyword, location or "") if part)
    if occupation_tokens(role_text) or (occupation is not None):
        if not title_matches_job_query(listing.title, role_text):
            return False
        blob = _fold_listing_text(listing.title, listing.location)
        for term in required_extra_terms(role_text):
            if term not in blob:
                return False
    elif keyword and not is_occupation_query(keyword):
        blob = _fold_listing_text(listing.title, listing.location)
        if _fold(keyword) not in blob:
            return False
    skip_country = is_border_place(location)
    if filters.country is not None and listing.country != filters.country and not skip_country:
        return False
    if filters.country == CountryCode.CH and location_in_neighbor_belt(listing.location):
        return False
    if filters.price_min is not None:
        if listing.price is None or listing.price < filters.price_min:
            return False
    if filters.price_max is not None:
        if listing.price is None or listing.price > filters.price_max:
            return False
    if filters.rooms_min is not None:
        if listing.rooms is None or listing.rooms < filters.rooms_min:
            return False
    if filters.property_type is not None:
        if listing.property_type is None or listing.property_type != filters.property_type:
            return False
    if filters.has_parking is True and listing.has_parking is False:
        return False
    if filters.has_parking is False and listing.has_parking is True:
        return False
    if filters.is_under_construction is True:
        if not listing_looks_under_construction(listing):
            return False
    if filters.is_under_construction is False:
        if listing_looks_under_construction(listing):
            return False
    if filters.job_category is not None:
        if not job_category_matches(listing.job_category, filters.job_category, listing.title):
            return False
    if filters.employment_type is not None and listing.employment_type is not None:
        if listing.employment_type != filters.employment_type:
            return False
    if filters.workload_min is not None or filters.workload_max is not None:
        if listing.workload_min is not None or listing.workload_max is not None:
            filter_min = filters.workload_min if filters.workload_min is not None else 0
            filter_max = filters.workload_max if filters.workload_max is not None else 100
            listing_min = listing.workload_min if listing.workload_min is not None else 0
            listing_max = listing.workload_max if listing.workload_max is not None else 100
            if listing_max < filter_min or listing_min > filter_max:
                return False
    provider_ids = filters.resolved_provider_ids()
    if provider_ids is not None and listing.provider_id not in provider_ids:
        return False
    return True
