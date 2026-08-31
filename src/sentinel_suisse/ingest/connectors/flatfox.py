"""Flatfox (SMG) — public REST JSON used by their map/app. No HTML scrape.

Two keyless endpoints power flatfox.ch search:

    GET https://flatfox.ch/api/v1/pin/?north=&south=&east=&west=
    GET https://flatfox.ch/api/v1/public-listing/{pk}/

Pin search is geo-filtered (one bbox per Swiss / border town). List search
ignores city/bbox and cannot filter by rooms, so we do not paginate the
nationwide 35k feed. Instead we walk the same city list as jobs and, inside
each box, take a mix of expensive pins first (family-size flats) then the
rest. Apply URL is always the Flatfox listing page.

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
_COUNTRY_MAP = {
    "CH": CountryCode.CH,
    "FR": CountryCode.FR,
    "DE": CountryCode.DE,
    "IT": CountryCode.IT,
}


def _box(lat: float, lon: float, span: float = 0.08) -> tuple[str, str, str, str]:
    """north, south, east, west around a city centre."""
    return (
        f"{lat + span:.2f}",
        f"{lat - span:.2f}",
        f"{lon + span:.2f}",
        f"{lon - span:.2f}",
    )


# north, south, east, west — metro boxes, then the same towns as the job crawl.
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
    "aarau": _box(47.39, 8.04),
    "morges": _box(46.51, 6.50, 0.06),
    "bulle": _box(46.62, 7.06),
    "martigny": _box(46.10, 7.07),
    "sierre": _box(46.29, 7.54),
    "monthey": _box(46.25, 6.95),
    "delemont": _box(47.36, 7.34),
    "olten": _box(47.35, 7.90),
    "baden": _box(47.47, 8.31),
    "wil": _box(47.46, 9.04),
    "frauenfeld": _box(47.56, 8.90),
    "solothurn": _box(47.21, 7.53),
    "langenthal": _box(47.22, 7.80),
    "interlaken": _box(46.69, 7.86),
    "liestal": _box(47.48, 7.73, 0.06),
    "kreuzlingen": _box(47.65, 9.18, 0.06),
    "locarno": _box(46.17, 8.80),
    "mendrisio": _box(45.87, 8.98, 0.06),
    "chiasso": _box(45.83, 9.03, 0.05),
    "bellinzona": _box(46.19, 9.02),
    "brig": _box(46.32, 7.99),
    "schwyz": _box(47.02, 8.65),
    "emmen": _box(47.08, 8.30, 0.05),
    "dietikon": _box(47.40, 8.40, 0.05),
    "horgen": _box(47.26, 8.60, 0.05),
    "annemasse": ("46.22", "46.16", "6.30", "6.18"),
    "ferney": _box(46.26, 6.11, 0.05),
    "stjulien": _box(46.14, 6.08, 0.05),
    "gaillard": _box(46.19, 6.21, 0.04),
    "thonon": _box(46.37, 6.48),
    "annecy": _box(45.90, 6.13, 0.10),
    "loerrach": _box(47.61, 7.66, 0.06),
    "weil": _box(47.59, 7.61, 0.05),
    "konstanz": _box(47.66, 9.18, 0.06),
    "waldshut": _box(47.62, 8.22, 0.06),
    "como": _box(45.81, 9.09, 0.08),
    "varese": _box(45.82, 8.83, 0.08),
    "domodossola": _box(46.12, 8.29, 0.08),
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
    if country != CountryCode.CH and country.value not in location:
        location = f"{location}, {country.value}"
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
    country = _COUNTRY_MAP.get(country_raw, CountryCode.CH)
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


def parse_pin_records(payload: Any) -> list[tuple[int, Decimal | None]]:
    if not isinstance(payload, list):
        msg = "Unexpected Flatfox pin response (expected a JSON list)"
        raise FlatfoxFetchError(msg)
    records: list[tuple[int, Decimal | None]] = []
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
            records.append((pk, price))
    return records


def parse_pin_list(payload: Any) -> list[int]:
    return [pk for pk, _price in parse_pin_records(payload)]


def select_pin_pks(records: list[tuple[int, Decimal | None]], limit: int) -> list[int]:
    """Prefer expensive pins (family-size homes) then fill with the rest.

    Map pins have no room count. Rent is the only signal, so the first half of
    the budget is the highest-priced ads — same idea as the job role-keyword pass.
    """
    if limit <= 0:
        return []
    if len(records) <= limit:
        return [pk for pk, _price in records]

    priced = [(pk, price) for pk, price in records if price is not None]
    priced.sort(key=lambda item: item[1], reverse=True)

    family_n = max(1, limit // 2)
    chosen: list[int] = []
    seen: set[int] = set()
    for pk, _price in priced[:family_n]:
        if pk not in seen:
            seen.add(pk)
            chosen.append(pk)
            if len(chosen) >= limit:
                return chosen

    for pk, _price in records:
        if pk in seen:
            continue
        seen.add(pk)
        chosen.append(pk)
        if len(chosen) >= limit:
            break
    return chosen[:limit]


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
    pause = max(0.0, settings.flatfox_request_pause_seconds)

    for north, south, east, west in boxes:
        if len(listings) >= total_cap:
            break
        try:
            time.sleep(pause)
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
        records = parse_pin_records(pin_payload)
        pks = select_pin_pks(records, min(per_region, remaining))
        for pk in pks:
            detail = _fetch_detail(headers, pk, pause)
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


def _fetch_detail(headers: dict[str, str], pk: int, pause: float) -> dict[str, Any] | None:
    try:
        time.sleep(pause)
        response = httpx.get(_DETAIL_URL.format(pk=pk), headers=headers, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None
