"""Flatfox (SMG) — public REST JSON used by their map/app. No HTML scrape.

Two keyless endpoints power flatfox.ch search:

    GET https://flatfox.ch/api/v1/pin/?north=&south=&east=&west=
    GET https://flatfox.ch/api/v1/public-listing/{pk}/

Pin search is geo-filtered (one bbox per Swiss region). List search ignores
city/bbox, so we do not paginate the nationwide 35k feed. Apply URL is always
the Flatfox listing page — LinkSwiss does not host applications.

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

# north, south, east, west — metro-scale boxes (not tiny city centres).
_REGION_BOXES: dict[str, tuple[str, str, str, str]] = {
    "zurich": ("47.48", "47.28", "8.75", "8.35"),
    "bern": ("47.05", "46.85", "7.55", "7.30"),
    "basel": ("47.62", "47.48", "7.72", "7.48"),
    "lausanne": ("46.62", "46.48", "6.78", "6.52"),
    "lugano": ("46.05", "45.95", "9.02", "8.88"),
    "luzern": ("47.10", "47.00", "8.40", "8.22"),
    "stgallen": ("47.48", "47.38", "9.45", "9.28"),
    "sion": ("46.28", "46.18", "7.42", "7.28"),
    "fribourg": ("46.85", "46.75", "7.22", "7.05"),
    "neuchatel": ("47.05", "46.95", "7.00", "6.82"),
    "winterthur": ("47.55", "47.45", "8.85", "8.65"),
    "nyon": ("46.42", "46.34", "6.30", "6.18"),
    "vevey": ("46.50", "46.44", "6.90", "6.78"),
    "montreux": ("46.48", "46.40", "6.98", "6.88"),
    "thun": ("46.80", "46.72", "7.68", "7.52"),
    "chur": ("46.88", "46.82", "9.58", "9.48"),
    "yverdon": ("46.82", "46.74", "6.70", "6.58"),
    "chauxdefonds": ("47.14", "47.06", "6.88", "6.76"),
    "biel": ("47.18", "47.10", "7.32", "7.18"),
    "zug": ("47.20", "47.12", "8.55", "8.45"),
    "schaffhausen": ("47.74", "47.66", "8.70", "8.58"),
    "uster": ("47.38", "47.32", "8.76", "8.66"),
    "annemasse": ("46.22", "46.16", "6.30", "6.18"),
}


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


def _format_location(city: Any, zipcode: Any, country: CountryCode) -> str | None:
    city_s = str(city).strip() if city else ""
    zip_s = str(zipcode).strip() if zipcode else ""
    folded = city_s.casefold().replace("è", "e").replace("é", "e").replace("ü", "u")
    if folded in {"geneve", "genf"}:
        city_s = "Geneva"
    elif folded == "zurich":
        city_s = "Zurich"
    parts = [part for part in (city_s, zip_s) if part]
    if not parts:
        return None
    location = ", ".join(parts)
    if country == CountryCode.FR and "FR" not in location:
        location = f"{location}, FR"
    return location[:200]


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

    country_raw = str(listing.get("country") or "CH").upper()
    country = CountryCode.FR if country_raw == "FR" else CountryCode.CH
    location = _format_location(listing.get("city"), listing.get("zipcode"), country)

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
        location=location,
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
    listings: list[RawListing] = []
    seen: set[str] = set()
    boxes = _iter_region_boxes(settings)
    if not boxes:
        return []
    total_cap = max(1, settings.flatfox_max_listings)
    # Share the budget across every region so Winterthur/Fribourg are not starved
    # after Geneva/Zurich fill the previous global cap first.
    fair_share = max(1, total_cap // len(boxes))
    per_region = min(max(1, settings.flatfox_max_per_region), fair_share)

    for north, south, east, west in boxes:
        if len(listings) >= total_cap:
            break
        try:
            time.sleep(settings.ingest_rate_limit_seconds)
            pin_response = httpx.get(
                _PIN_URL,
                params={"north": north, "south": south, "east": east, "west": west},
                headers=headers,
                timeout=30.0,
            )
            pin_response.raise_for_status()
            pin_payload = pin_response.json()
        except httpx.HTTPError as exc:
            msg = f"Flatfox pin request failed: {exc}"
            raise FlatfoxFetchError(msg) from exc
        except ValueError as exc:
            msg = f"Flatfox pin response was not valid JSON: {exc}"
            raise FlatfoxFetchError(msg) from exc

        remaining = total_cap - len(listings)
        pks = parse_pin_list(pin_payload)[: min(per_region, remaining)]
        for pk in pks:
            detail = _fetch_detail(settings, headers, pk)
            if detail is None:
                continue
            mapped = map_public_listing(detail)
            if mapped is None or mapped.external_id in seen:
                continue
            seen.add(mapped.external_id)
            listings.append(mapped)
            if len(listings) >= total_cap:
                break
    return listings


def _iter_region_boxes(settings: Settings) -> list[tuple[str, str, str, str]]:
    names = [item.strip().lower() for item in settings.flatfox_regions.split(",") if item.strip()]
    if not names:
        names = ["geneva"]
    boxes: list[tuple[str, str, str, str]] = []
    for name in names:
        if name == "geneva":
            boxes.append(
                (
                    settings.flatfox_north,
                    settings.flatfox_south,
                    settings.flatfox_east,
                    settings.flatfox_west,
                )
            )
            continue
        box = _REGION_BOXES.get(name)
        if box is not None:
            boxes.append(box)
    return boxes or [
        (
            settings.flatfox_north,
            settings.flatfox_south,
            settings.flatfox_east,
            settings.flatfox_west,
        )
    ]


def _fetch_detail(settings: Settings, headers: dict[str, str], pk: int) -> dict[str, Any] | None:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(_DETAIL_URL.format(pk=pk), headers=headers, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None
