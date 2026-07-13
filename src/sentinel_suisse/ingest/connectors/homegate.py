"""Extract listings from Homegate search page embedded JSON."""

import json
import time
from decimal import Decimal
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import ListingType

_HOMEGATE_BASE = "https://www.homegate.ch"
_STATE_MARKER = "window.__INITIAL_STATE__="


class HomegateFetchError(RuntimeError):
    """Homegate HTTP or parse failure."""


class HomegateDisabledError(RuntimeError):
    """Live Homegate ingest is not enabled in settings."""


def extract_initial_state(html: str) -> dict[str, Any]:
    idx = html.find(_STATE_MARKER)
    if idx == -1:
        msg = "Homegate __INITIAL_STATE__ not found in HTML"
        raise HomegateFetchError(msg)
    json_start = idx + len(_STATE_MARKER)
    try:
        state, _end = json.JSONDecoder().raw_decode(html, json_start)
    except json.JSONDecodeError as exc:
        msg = "Homegate __INITIAL_STATE__ is not valid JSON"
        raise HomegateFetchError(msg) from exc
    if not isinstance(state, dict):
        msg = "Homegate __INITIAL_STATE__ must be a JSON object"
        raise HomegateFetchError(msg)
    return state


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    listings_raw = (
        state.get("resultList", {})
        .get("search", {})
        .get("fullSearch", {})
        .get("result", {})
        .get("listings", [])
    )
    if not isinstance(listings_raw, list):
        msg = "Unexpected Homegate search state shape"
        raise HomegateFetchError(msg)

    parsed: list[RawListing] = []
    for entry in listings_raw:
        listing = entry.get("listing") if isinstance(entry, dict) else None
        if not isinstance(listing, dict):
            continue
        raw = _map_listing(listing)
        if raw is not None:
            parsed.append(raw)
    return parsed


def _map_listing(listing: dict[str, Any]) -> RawListing | None:
    listing_id = listing.get("id")
    if listing_id is None:
        return None

    title = _pick_title(listing)
    if not title:
        return None

    location = _pick_location(listing)
    price = _pick_price(listing)
    source_url = _pick_source_url(listing, listing_id)
    listing_type = _pick_listing_type(listing)

    return RawListing(
        external_id=str(listing_id),
        listing_type=listing_type,
        title=title[:300],
        description=_pick_description(listing),
        location=location,
        price=price,
        source_url=source_url,
        raw_payload={"source": "homegate", "listing_id": listing_id},
    )


def _pick_title(listing: dict[str, Any]) -> str | None:
    localization = listing.get("localization")
    if isinstance(localization, dict):
        primary = localization.get("primary")
        if isinstance(primary, str) and isinstance(localization.get(primary), dict):
            text = localization[primary].get("text")
            if isinstance(text, dict) and text.get("title"):
                return str(text["title"])
        for locale_data in localization.values():
            if isinstance(locale_data, dict):
                text = locale_data.get("text")
                if isinstance(text, dict) and text.get("title"):
                    return str(text["title"])
    return listing.get("title") if listing.get("title") else None


def _pick_description(listing: dict[str, Any]) -> str | None:
    localization = listing.get("localization")
    if isinstance(localization, dict):
        for locale_data in localization.values():
            if isinstance(locale_data, dict):
                text = locale_data.get("text")
                if isinstance(text, dict) and text.get("description"):
                    desc = str(text["description"])
                    return desc[:10000]
    return None


def _pick_location(listing: dict[str, Any]) -> str | None:
    address = listing.get("address")
    if not isinstance(address, dict):
        return None
    parts = [address.get("locality"), address.get("postalCode")]
    cleaned = [str(part) for part in parts if part]
    return ", ".join(cleaned)[:200] if cleaned else None


def _pick_price(listing: dict[str, Any]) -> Decimal | None:
    prices = listing.get("prices")
    if not isinstance(prices, dict):
        return None
    for key in ("rent", "buy"):
        bucket = prices.get(key)
        if not isinstance(bucket, dict):
            continue
        for field in ("net", "gross", "price"):
            value = bucket.get(field)
            if value is not None:
                return Decimal(str(value))
    return None


def _pick_listing_type(listing: dict[str, Any]) -> ListingType:
    raw = str(listing.get("listingType", "")).upper()
    if raw in {"RENT", "RENTAL", "MIETEN"}:
        return ListingType.HOUSING
    return ListingType.HOUSING


def _pick_source_url(listing: dict[str, Any], listing_id: Any) -> str:
    meta = listing.get("meta")
    if isinstance(meta, dict) and meta.get("url"):
        path = str(meta["url"])
        if path.startswith("http"):
            return path
        return f"{_HOMEGATE_BASE}{path}"
    return f"{_HOMEGATE_BASE}/mieten/{listing_id}"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_homegate_live:
        msg = "Live Homegate ingest is disabled (set INGEST_HOMEGATE_LIVE=true)"
        raise HomegateDisabledError(msg)

    url = search_url or settings.homegate_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"Homegate request failed: {exc}"
        raise HomegateFetchError(msg) from exc

    state = extract_initial_state(response.text)
    return parse_search_state(state)
