"""Match listings against saved search filters."""

from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.job_taxonomy import job_category_matches
from sentinel_suisse.services.listing_freshness import listing_is_fresh
from sentinel_suisse.services.location_match import location_matches


def listing_matches_query(listing: Listing, filters: SearchQuery) -> bool:
    if not listing_is_fresh(listing):
        return False
    if listing.is_hidden:
        return False
    if filters.listing_type is not None and listing.listing_type != filters.listing_type:
        return False
    if filters.location is not None:
        in_place = location_matches(listing.location, filters.location)
        needle = filters.location.strip().casefold()
        hay = f"{listing.title or ''} {listing.description or ''}".casefold()
        if not in_place and needle not in hay:
            return False
    if filters.country is not None and listing.country != filters.country:
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
        if listing.is_under_construction is not True:
            return False
    if filters.is_under_construction is False:
        if listing.is_under_construction is True:
            return False
    if filters.job_category is not None:
        hay = f"{listing.title or ''} {listing.description or ''}"
        if not job_category_matches(listing.job_category, filters.job_category, hay):
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
