"""Match listings against saved search filters."""

from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery


def listing_matches_query(listing: Listing, filters: SearchQuery) -> bool:
    if filters.listing_type is not None and listing.listing_type != filters.listing_type:
        return False
    if filters.location is not None:
        if listing.location is None:
            return False
        if filters.location.lower() not in listing.location.lower():
            return False
    if filters.price_min is not None:
        if listing.price is None or listing.price < filters.price_min:
            return False
    if filters.price_max is not None:
        if listing.price is None or listing.price > filters.price_max:
            return False
    if filters.provider_id is not None and listing.provider_id != filters.provider_id:
        return False
    return True
