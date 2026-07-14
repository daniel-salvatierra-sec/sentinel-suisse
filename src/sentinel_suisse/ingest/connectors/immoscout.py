"""Extract listings from ImmoScout24.ch search page embedded JSON."""

import time
from decimal import Decimal
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import EmbedParseError, extract_first_state
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import ListingType

_IMMOSCOUT_BASE = "https://www.immoscout24.ch"
_STATE_MARKERS = (
    "window.__INITIAL_STATE__=",
    "window.__NEXT_DATA__=",
    "window.__PINIA_INITIAL_STATE__=",
)

_LISTING_PATHS: tuple[tuple[str, ...], ...] = (
    ("resultList", "listData"),
    ("resultList", "listings"),
    ("search", "results"),
    ("search", "listings"),
    ("listings",),
    ("results",),
    ("props", "pageProps", "listings"),
    ("props", "pageProps", "resultList", "listData"),
)


class ImmoscoutFetchError(RuntimeError):
    """ImmoScout24 HTTP or parse failure."""


class ImmoscoutDisabledError(RuntimeError):
    """Live ImmoScout24 ingest is not enabled in settings."""


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    listings_raw = _find_listings(state)
    if listings_raw is None:
        msg = "Unexpected ImmoScout24 search state shape"
        raise ImmoscoutFetchError(msg)

    parsed: list[RawListing] = []
    for entry in listings_raw:
        if not isinstance(entry, dict):
            continue
        raw = _map_listing(entry)
        if raw is not None:
            parsed.append(raw)
    return parsed


def _find_listings(state: dict[str, Any]) -> list[Any] | None:
    for path in _LISTING_PATHS:
        node: Any = state
        for key in path:
            if not isinstance(node, dict):
                node = None
                break
            node = node.get(key)
        if isinstance(node, list):
            return node
    return None


def _map_listing(listing: dict[str, Any]) -> RawListing | None:
    listing_id = (
        listing.get("id")
        or listing.get("listingId")
        or listing.get("advertisementId")
        or listing.get("offerId")
    )
    title = listing.get("title") or listing.get("name") or listing.get("headline")
    if listing_id is None or not title:
        return None

    return RawListing(
        external_id=str(listing_id),
        listing_type=ListingType.HOUSING,
        title=str(title)[:300],
        description=_pick_description(listing),
        location=_pick_location(listing),
        price=_pick_price(listing),
        source_url=_pick_source_url(listing, listing_id),
        raw_payload={"source": "immoscout", "listing_id": str(listing_id)},
    )


def _pick_description(listing: dict[str, Any]) -> str | None:
    for key in ("description", "summary", "text", "teaser"):
        value = listing.get(key)
        if value:
            return str(value)[:10000]
    return None


def _pick_location(listing: dict[str, Any]) -> str | None:
    address = listing.get("address")
    if isinstance(address, dict):
        parts = [
            address.get("locality") or address.get("city") or address.get("town"),
            address.get("postalCode") or address.get("zip"),
        ]
        cleaned = [str(part) for part in parts if part]
        if cleaned:
            return ", ".join(cleaned)[:200]
    for key in ("location", "city", "place", "geoLocation"):
        value = listing.get(key)
        if isinstance(value, dict):
            name = value.get("name") or value.get("city")
            if name:
                return str(name)[:200]
        elif value:
            return str(value)[:200]
    return None


def _pick_price(listing: dict[str, Any]) -> Decimal | None:
    price = listing.get("price")
    if isinstance(price, dict):
        for key in ("gross", "rent", "amount", "sellingPrice"):
            value = price.get(key)
            if value is not None:
                return Decimal(str(value))
    for key in ("rent_gross", "rent", "price", "monthly_rent", "grossRent"):
        value = listing.get(key)
        if value is not None and not isinstance(value, dict):
            return Decimal(str(value))
    return None


def _pick_source_url(listing: dict[str, Any], listing_id: Any) -> str:
    for key in ("detailUrl", "url", "link", "permalink"):
        value = listing.get(key)
        if value:
            path = str(value)
            if path.startswith("http"):
                return path
            return f"{_IMMOSCOUT_BASE}{path}"
    return f"{_IMMOSCOUT_BASE}/fr/d/{listing_id}"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_immoscout_live:
        msg = "Live ImmoScout24 ingest is disabled (set INGEST_IMMOSCOUT_LIVE=true)"
        raise ImmoscoutDisabledError(msg)

    url = search_url or settings.immoscout_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"ImmoScout24 request failed: {exc}"
        raise ImmoscoutFetchError(msg) from exc

    try:
        state = extract_first_state(response.text, _STATE_MARKERS)
    except EmbedParseError as exc:
        msg = f"ImmoScout24 embedded state parse failed: {exc}"
        raise ImmoscoutFetchError(msg) from exc

    return parse_search_state(state)
