"""Extract listings from Leboncoin (FR) search page embedded JSON."""

import time
from decimal import Decimal
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import EmbedParseError, extract_first_state
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, ListingType, PropertyType

_LEBONCOIN_BASE = "https://www.leboncoin.fr"
_STATE_MARKERS = (
    "window.__NEXT_DATA__=",
    "window.__INITIAL_STATE__=",
    "window.__PRELOADED_STATE__=",
)

_LISTING_PATHS: tuple[tuple[str, ...], ...] = (
    ("props", "pageProps", "ads"),
    ("props", "pageProps", "searchData", "ads"),
    ("props", "pageProps", "listings"),
    ("ads",),
    ("search", "ads"),
    ("listings",),
)


class LeboncoinFetchError(RuntimeError):
    """Leboncoin HTTP or parse failure."""


class LeboncoinDisabledError(RuntimeError):
    """Live Leboncoin ingest is not enabled in settings."""


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    listings_raw = _find_listings(state)
    if listings_raw is None:
        msg = "Unexpected Leboncoin search state shape"
        raise LeboncoinFetchError(msg)

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
    listing_id = listing.get("list_id") or listing.get("id") or listing.get("ad_id")
    title = listing.get("subject") or listing.get("title") or listing.get("name")
    if listing_id is None or not title:
        return None

    return RawListing(
        external_id=str(listing_id),
        listing_type=ListingType.HOUSING,
        title=str(title)[:300],
        description=_pick_description(listing),
        location=_pick_location(listing),
        country=CountryCode.FR,
        price=_pick_price(listing),
        rooms=_pick_rooms(listing),
        property_type=_pick_property_type(listing),
        has_parking=_pick_parking(listing),
        source_url=_pick_source_url(listing, listing_id),
        raw_payload={"source": "leboncoin", "listing_id": str(listing_id)},
    )


def _pick_description(listing: dict[str, Any]) -> str | None:
    for key in ("body", "description", "text"):
        value = listing.get(key)
        if value:
            return str(value)[:10000]
    return None


def _pick_location(listing: dict[str, Any]) -> str | None:
    location = listing.get("location")
    if isinstance(location, dict):
        parts = [
            location.get("city") or location.get("city_label"),
            location.get("zipcode") or location.get("department_name"),
        ]
        cleaned = [str(part) for part in parts if part]
        if cleaned:
            return ", ".join(cleaned)[:200]
    for key in ("city", "place"):
        value = listing.get(key)
        if value:
            return str(value)[:200]
    return None


def _pick_price(listing: dict[str, Any]) -> Decimal | None:
    price = listing.get("price")
    if isinstance(price, list) and price:
        return Decimal(str(price[0]))
    if price is not None and not isinstance(price, dict | list):
        return Decimal(str(price))
    price_cents = listing.get("price_cents")
    if price_cents is not None:
        return Decimal(str(price_cents)) / Decimal("100")
    return None


def _pick_rooms(listing: dict[str, Any]) -> Decimal | None:
    attrs = listing.get("attributes")
    if isinstance(attrs, list):
        for attr in attrs:
            if not isinstance(attr, dict):
                continue
            key = str(attr.get("key") or attr.get("name") or "").lower()
            if key in {"rooms", "rooms_count", "nb_rooms"}:
                value = attr.get("value") or attr.get("value_label")
                if value is not None:
                    try:
                        return Decimal(str(value).replace(",", "."))
                    except (ValueError, ArithmeticError):
                        return None
    for key in ("rooms", "rooms_count"):
        value = listing.get(key)
        if value is not None:
            return Decimal(str(value))
    return None


def _pick_property_type(listing: dict[str, Any]) -> PropertyType | None:
    raw = listing.get("category_name") or listing.get("real_estate_type") or listing.get("type")
    if raw is None:
        return None
    text = str(raw).lower()
    if "studio" in text:
        return PropertyType.STUDIO
    if "maison" in text or "house" in text:
        return PropertyType.HOUSE
    if "chambre" in text or "room" in text:
        return PropertyType.ROOM
    if "appart" in text or "flat" in text:
        return PropertyType.APARTMENT
    return PropertyType.OTHER


def _pick_parking(listing: dict[str, Any]) -> bool | None:
    attrs = listing.get("attributes")
    if isinstance(attrs, list):
        for attr in attrs:
            if not isinstance(attr, dict):
                continue
            key = str(attr.get("key") or "").lower()
            if "parking" in key or "garage" in key:
                value = attr.get("value")
                if isinstance(value, bool):
                    return value
                if value is not None:
                    return str(value).lower() in {"1", "true", "oui", "yes"}
    return None


def _pick_source_url(listing: dict[str, Any], listing_id: Any) -> str:
    for key in ("url", "link"):
        value = listing.get(key)
        if value:
            path = str(value)
            if path.startswith("http"):
                return path
            return f"{_LEBONCOIN_BASE}{path}"
    return f"{_LEBONCOIN_BASE}/ad/{listing_id}"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_leboncoin_live:
        msg = "Live Leboncoin ingest is disabled (set INGEST_LEBONCOIN_LIVE=true)"
        raise LeboncoinDisabledError(msg)

    url = search_url or settings.leboncoin_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"Leboncoin request failed: {exc}"
        raise LeboncoinFetchError(msg) from exc

    try:
        state = extract_first_state(response.text, _STATE_MARKERS)
    except EmbedParseError as exc:
        msg = f"Leboncoin embedded state parse failed: {exc}"
        raise LeboncoinFetchError(msg) from exc

    return parse_search_state(state)
