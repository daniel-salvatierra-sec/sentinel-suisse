"""STMicroelectronics (Geneva HQ) — Eightfold public careers JSON API, no scraping.

The company's career site (stmicroelectronics.eightfold.ai) is an Eightfold SmartApply
app. The same JSON endpoints the site's own UI calls are public and keyless:

    GET {tenant}.eightfold.ai/api/apply/v2/jobs?domain={domain}&start=0&num=50
    GET {tenant}.eightfold.ai/api/apply/v2/jobs/{id}?domain={domain}

List items omit the description (`job_description` is empty); the detail endpoint
returns the full text. ST posts globally (~480 roles); we filter to CH/FR/DE/IT using
the list-level `location` string *before* fetching details, so India/Singapore/US
roles never cost a detail request.

See docs/providers/stmicroelectronics.md.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.workday import pick_employment_type, strip_html
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, ListingType

_TENANT = "stmicroelectronics"
_DOMAIN = "stmicroelectronics.com"
_LIST_URL = f"https://{_TENANT}.eightfold.ai/api/apply/v2/jobs"
_DETAIL_URL = f"https://{_TENANT}.eightfold.ai/api/apply/v2/jobs/{{job_id}}"
_PAGE_SIZE = 50
_SLUG = "stmicroelectronics"

_CH_MARKERS = (
    "switzerland",
    "suisse",
    "schweiz",
    "geneva",
    "genève",
    "geneve",
    "plan-les-ouates",
    "plan les ouates",
    "meyrin",
)
_FR_MARKERS = ("france",)
_DE_MARKERS = ("germany", "deutschland", "allemagne", "munich", "münchen")
_IT_MARKERS = ("italy", "italia", "italie", "agrate", "catania", "milan", "milano")


class STMicroelectronicsFetchError(RuntimeError):
    """Eightfold API HTTP or parse failure."""


class STMicroelectronicsDisabledError(RuntimeError):
    """Live STMicroelectronics ingest is not enabled in settings."""


def pick_country(location: str | None) -> CountryCode | None:
    if not location:
        return None
    lowered = location.lower()
    if any(marker in lowered for marker in _CH_MARKERS):
        return CountryCode.CH
    if any(marker in lowered for marker in _FR_MARKERS):
        return CountryCode.FR
    if any(marker in lowered for marker in _DE_MARKERS):
        return CountryCode.DE
    if any(marker in lowered for marker in _IT_MARKERS):
        return CountryCode.IT
    return None


def _city_from_location(location: str) -> str:
    city = location.split(",")[0].strip()
    return {
        "Genève": "Geneva",
        "Geneve": "Geneva",
    }.get(city, city)


def _fetch_detail(settings: Settings, job_id: int | str) -> dict[str, Any] | None:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(
            _DETAIL_URL.format(job_id=job_id),
            params={"domain": _DOMAIN, "hl": "en"},
            headers={"Accept": "application/json", "User-Agent": settings.ingest_user_agent},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        return None


def map_position(item: dict[str, Any], settings: Settings) -> RawListing | None:
    job_id = item.get("id")
    title = item.get("name") or item.get("posting_name")
    location = item.get("location")
    if not job_id or not title:
        return None

    country = pick_country(str(location) if location else None)
    if country is None:
        return None

    detail = _fetch_detail(settings, job_id)
    description = None
    source_url = item.get("canonicalPositionUrl")
    department = item.get("department")
    if isinstance(detail, dict):
        raw_description = detail.get("job_description")
        if raw_description:
            description = strip_html(str(raw_description))
        source_url = detail.get("canonicalPositionUrl") or source_url
        department = detail.get("department") or department

    if not source_url:
        source_url = f"https://{_TENANT}.eightfold.ai/careers/job/{job_id}"

    city = _city_from_location(str(location)) if location else None

    return RawListing(
        external_id=f"{_SLUG}-{job_id}",
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=description[:10000] if description else None,
        location=city[:200] if city else None,
        country=country,
        price=None,
        job_category=str(department)[:80] if department else None,
        employment_type=pick_employment_type(str(title)),
        source_url=str(source_url),
        raw_payload={"source": _SLUG, "eightfold_id": job_id},
    )


def parse_list_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    positions = payload.get("positions")
    if not isinstance(positions, list):
        msg = "Unexpected Eightfold list response shape (missing 'positions')"
        raise STMicroelectronicsFetchError(msg)

    parsed: list[RawListing] = []
    for item in positions:
        if not isinstance(item, dict):
            continue
        raw = map_position(item, settings)
        if raw is not None:
            parsed.append(raw)
    return parsed


def _fetch_list_page(settings: Settings, start: int) -> dict[str, Any]:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(
            _LIST_URL,
            params={"domain": _DOMAIN, "start": start, "num": _PAGE_SIZE},
            headers={"Accept": "application/json", "User-Agent": settings.ingest_user_agent},
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"STMicroelectronics Eightfold list request failed: {exc}"
        raise STMicroelectronicsFetchError(msg) from exc

    try:
        return response.json()
    except ValueError as exc:
        msg = f"STMicroelectronics Eightfold list response was not valid JSON: {exc}"
        raise STMicroelectronicsFetchError(msg) from exc


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query ST's public Eightfold JSON API. `search_url` unused — CLI signature."""
    if not settings.ingest_stmicroelectronics_live:
        msg = "Live STMicroelectronics ingest is disabled (set INGEST_STMICROELECTRONICS_LIVE=true)"
        raise STMicroelectronicsDisabledError(msg)

    all_items: list[RawListing] = []
    start = 0
    while True:
        payload = _fetch_list_page(settings, start)
        all_items.extend(parse_list_page(payload, settings))
        positions = payload.get("positions") or []
        total = int(payload.get("count") or 0)
        start += len(positions) if isinstance(positions, list) else _PAGE_SIZE
        if not positions or start >= total:
            break

    return all_items
