"""Extract listings from newhome.ch search page embedded JSON."""

import time
from decimal import Decimal
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import EmbedParseError, extract_first_state
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import ListingType, PropertyType

_NEWHOME_BASE = "https://www.newhome.ch"
_STATE_MARKERS = (
    "window.__INITIAL_STATE__=",
    "window.__NEXT_DATA__=",
    "window.__NUXT__=",
)

_LISTING_PATHS: tuple[tuple[str, ...], ...] = (
    ("search", "results"),
    ("search", "listings"),
    ("props", "pageProps", "listings"),
    ("props", "pageProps", "search", "results"),
    ("listings",),
    ("results",),
)


class NewhomeFetchError(RuntimeError):
    """newhome.ch HTTP or parse failure."""


class NewhomeDisabledError(RuntimeError):
    """Live newhome.ch ingest is not enabled in settings."""


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    listings_raw = _find_listings(state)
    if listings_raw is None:
        msg = "Unexpected newhome.ch search state shape"
        raise NewhomeFetchError(msg)

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
    listing_id = listing.get("id") or listing.get("listingId") or listing.get("objectId")
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
        rooms=_pick_rooms(listing),
        property_type=_pick_property_type(listing),
        has_parking=_pick_parking(listing),
        source_url=_pick_source_url(listing, listing_id),
        raw_payload={"source": "newhome", "listing_id": str(listing_id)},
    )


def _pick_description(listing: dict[str, Any]) -> str | None:
    for key in ("description", "summary", "text"):
        value = listing.get(key)
        if value:
            return str(value)[:10000]
    return None


def _pick_location(listing: dict[str, Any]) -> str | None:
    address = listing.get("address")
    if isinstance(address, dict):
        city = address.get("city") or address.get("locality")
        zip_code = address.get("zip") or address.get("postalCode")
        cleaned = [str(part) for part in (city, zip_code) if part]
        if cleaned:
            return ", ".join(cleaned)[:200]
    for key in ("location", "city", "place", "town"):
        value = listing.get(key)
        if value:
            return str(value)[:200]
    return None


def _pick_price(listing: dict[str, Any]) -> Decimal | None:
    for key in ("rent", "price", "rentGross", "rent_gross", "monthlyRent"):
        value = listing.get(key)
        if value is not None and not isinstance(value, dict):
            return Decimal(str(value))
    return None


def _pick_rooms(listing: dict[str, Any]) -> Decimal | None:
    for key in ("rooms", "numberOfRooms", "roomCount"):
        value = listing.get(key)
        if value is not None:
            return Decimal(str(value))
    return None


def _pick_property_type(listing: dict[str, Any]) -> PropertyType | None:
    raw = listing.get("propertyType") or listing.get("objectType") or listing.get("type")
    if raw is None:
        return None
    text = str(raw).lower()
    if "studio" in text:
        return PropertyType.STUDIO
    if "house" in text or "maison" in text or "haus" in text:
        return PropertyType.HOUSE
    if "room" in text or "zimmer" in text or "chambre" in text:
        return PropertyType.ROOM
    if "apartment" in text or "flat" in text or "wohnung" in text or "appartement" in text:
        return PropertyType.APARTMENT
    return PropertyType.OTHER


def _pick_parking(listing: dict[str, Any]) -> bool | None:
    for key in ("hasParking", "parking", "garage"):
        value = listing.get(key)
        if isinstance(value, bool):
            return value
    return None


def _pick_source_url(listing: dict[str, Any], listing_id: Any) -> str:
    for key in ("url", "detailUrl", "link", "permalink"):
        value = listing.get(key)
        if value:
            path = str(value)
            if path.startswith("http"):
                return path
            return f"{_NEWHOME_BASE}{path}"
    return f"{_NEWHOME_BASE}/fr/louer/detail/{listing_id}"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_newhome_live:
        msg = "Live newhome.ch ingest is disabled (set INGEST_NEWHOME_LIVE=true)"
        raise NewhomeDisabledError(msg)

    url = search_url or settings.newhome_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"newhome.ch request failed: {exc}"
        raise NewhomeFetchError(msg) from exc

    try:
        state = extract_first_state(response.text, _STATE_MARKERS)
    except EmbedParseError as exc:
        msg = f"newhome.ch embedded state parse failed: {exc}"
        raise NewhomeFetchError(msg) from exc

    return parse_search_state(state)
