"""Flatfox (SMG) — public REST JSON used by their map/app. No HTML scrape.

Two keyless endpoints power flatfox.ch search:

    GET https://flatfox.ch/api/v1/pin/?north=&south=&east=&west=
    GET https://flatfox.ch/api/v1/public-listing/{pk}/

Pin search is geo-filtered (Geneva + border). List search ignores city/bbox, so we
do not paginate the nationwide 35k feed. Apply URL is always the Flatfox listing
page — LinkSwiss does not host applications.

Documented API: https://flatfox.ch/docs/api/  robots.txt allows /. Live ingest stays
opt-in (`INGEST_FLATFOX_LIVE`). See docs/providers/flatfox.md.
"""

from __future__ import annotations

import time
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, ListingType, PropertyType

_PIN_URL = "https://flatfox.ch/api/v1/pin/"
_DETAIL_URL = "https://flatfox.ch/api/v1/public-listing/{pk}/"
_SITE = "https://flatfox.ch"

_SKIP_CATEGORIES = frozenset({"PARK", "INDUSTRY", "GASTRO", "AGRICULTURE"})
_MIN_MONTHLY_CHF = Decimal("500")


class FlatfoxFetchError(RuntimeError):
    """Flatfox HTTP or parse failure."""


class FlatfoxDisabledError(RuntimeError):
    """Live Flatfox ingest is not enabled in settings."""


def _as_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if number < 0:
        return None
    return number


def _property_type(category: str | None, object_type: str | None) -> PropertyType:
    cat = (category or "").upper()
    obj = (object_type or "").upper()
    if cat == "SHARED" or "SHARED" in obj or "ROOM" in obj:
        return PropertyType.ROOM
    if cat == "HOUSE" or "HOUSE" in obj:
        return PropertyType.HOUSE
    if "STUDIO" in obj:
        return PropertyType.STUDIO
    if cat == "APARTMENT" or "APART" in obj:
        return PropertyType.APARTMENT
    return PropertyType.OTHER


def _has_parking(listing: dict[str, Any]) -> bool | None:
    attrs = listing.get("attributes")
    if not isinstance(attrs, list):
        return None
    names = []
    for item in attrs:
        if isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]).lower())
    if not names:
        return None
    return any("park" in name or "garage" in name for name in names)


def _source_url(listing: dict[str, Any], listing_id: Any) -> str:
    path = listing.get("url")
    if isinstance(path, str) and path.startswith("http"):
        return path
    if isinstance(path, str) and path.startswith("/"):
        return f"{_SITE}{path}"
    return f"{_SITE}/en/flat/{listing_id}/"


def map_public_listing(listing: dict[str, Any]) -> RawListing | None:
    listing_id = listing.get("pk")
    if listing_id is None:
        return None
    if listing.get("offer_type") not in (None, "RENT"):
        return None
    category = str(listing.get("object_category") or "")
    if category.upper() in _SKIP_CATEGORIES:
        return None

    title = (
        listing.get("public_title")
        or listing.get("short_title")
        or listing.get("pitch_title")
        or listing.get("description_title")
    )
    if not title:
        return None

    price = _as_decimal(listing.get("rent_gross")) or _as_decimal(listing.get("price_display"))
    if listing.get("price_unit") == "yearlym2":
        return None
    if price is not None and price < _MIN_MONTHLY_CHF:
        return None

    city = listing.get("city")
    zipcode = listing.get("zipcode")
    location_parts = [str(part) for part in (city, zipcode) if part]
    country_raw = str(listing.get("country") or "CH").upper()
    country = CountryCode.FR if country_raw == "FR" else CountryCode.CH

    rooms = _as_decimal(listing.get("number_of_rooms"))
    property_type = _property_type(category, str(listing.get("object_type") or ""))
    if rooms is not None and rooms <= 1 and property_type == PropertyType.APARTMENT:
        property_type = PropertyType.STUDIO

    description = listing.get("description")
    return RawListing(
        external_id=str(listing_id),
        listing_type=ListingType.HOUSING,
        title=str(title)[:300],
        description=str(description)[:10000] if description else None,
        location=", ".join(location_parts)[:200] if location_parts else None,
        country=country,
        price=price,
        rooms=rooms if rooms is not None and rooms <= 20 else None,
        property_type=property_type,
        has_parking=_has_parking(listing),
        source_url=_source_url(listing, listing_id),
        raw_payload={"source": "flatfox", "listing_id": str(listing_id)},
    )


def parse_pin_list(payload: Any) -> list[int]:
    if not isinstance(payload, list):
        msg = "Unexpected Flatfox pin response (expected a JSON list)"
        raise FlatfoxFetchError(msg)
    pks: list[int] = []
    seen: set[int] = set()
    for pin in payload:
        if not isinstance(pin, dict):
            continue
        if pin.get("price_unit") in {"yearlym2", "sell"}:
            continue
        price = _as_decimal(pin.get("price_display"))
        if price is not None and price < _MIN_MONTHLY_CHF:
            continue
        pk = pin.get("pk")
        if isinstance(pk, int) and pk not in seen:
            seen.add(pk)
            pks.append(pk)
    return pks


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """`search_url` unused — kept to match the ingest CLI fetcher signature."""
    del search_url
    if not settings.ingest_flatfox_live:
        msg = "Live Flatfox ingest is disabled (set INGEST_FLATFOX_LIVE=true)"
        raise FlatfoxDisabledError(msg)

    headers = {"User-Agent": settings.ingest_user_agent, "Accept": "application/json"}
    params = {
        "north": settings.flatfox_north,
        "south": settings.flatfox_south,
        "east": settings.flatfox_east,
        "west": settings.flatfox_west,
    }
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        pin_response = httpx.get(_PIN_URL, params=params, headers=headers, timeout=30.0)
        pin_response.raise_for_status()
        pin_payload = pin_response.json()
    except httpx.HTTPError as exc:
        msg = f"Flatfox pin request failed: {exc}"
        raise FlatfoxFetchError(msg) from exc
    except ValueError as exc:
        msg = f"Flatfox pin response was not valid JSON: {exc}"
        raise FlatfoxFetchError(msg) from exc

    pks = parse_pin_list(pin_payload)[: settings.flatfox_max_listings]
    listings: list[RawListing] = []
    for pk in pks:
        detail = _fetch_detail(settings, headers, pk)
        if detail is None:
            continue
        mapped = map_public_listing(detail)
        if mapped is not None:
            listings.append(mapped)
    return listings


def _fetch_detail(settings: Settings, headers: dict[str, str], pk: int) -> dict[str, Any] | None:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(_DETAIL_URL.format(pk=pk), headers=headers, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None
