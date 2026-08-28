"""Shared parsing for JobCloud portals (jobup.ch, jobs.ch)."""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Iterator
from typing import Any
from urllib.parse import urlencode

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import (
    EmbedParseError,
    extract_first_state,
    extract_json_ld_job_postings,
)
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import EmploymentType, ListingType
from sentinel_suisse.services.job_taxonomy import classify_job_category

_WORKLOAD_RE = re.compile(r"(\d{1,3})\s*(?:[-–/]\s*(\d{1,3}))?\s*%")


def parse_jobcloud_search_html(
    html: str,
    *,
    source: str,
    base_url: str,
    state_markers: tuple[str, ...],
    parse_state: Callable[[dict[str, Any]], list[RawListing]],
    default_detail_path: str,
) -> list[RawListing]:
    """Legacy embedded state first, then schema.org JSON-LD (current JobCloud SSR)."""
    try:
        state = extract_first_state(html, state_markers)
    except EmbedParseError:
        try:
            postings = extract_json_ld_job_postings(html)
        except EmbedParseError as exc:
            msg = "No supported embedded state or JSON-LD JobPosting list in HTML"
            raise EmbedParseError(msg) from exc
        parsed: list[RawListing] = []
        for posting in postings:
            raw = map_json_ld_job_posting(
                posting,
                source=source,
                base_url=base_url,
                default_detail_path=default_detail_path,
            )
            if raw is not None:
                parsed.append(raw)
        return parsed
    return parse_state(state)


def map_json_ld_job_posting(
    posting: dict[str, Any],
    *,
    source: str,
    base_url: str,
    default_detail_path: str,
) -> RawListing | None:
    title = posting.get("title")
    if not title:
        return None

    job_id = _pick_job_id(posting)
    if job_id is None:
        return None

    company = _pick_hiring_organization(posting)
    description = posting.get("description")
    if description is None and company:
        description = company

    title_str = str(title)[:300]
    workload_min, workload_max = workload_from_title(title_str)
    return RawListing(
        external_id=str(job_id),
        listing_type=ListingType.JOB,
        title=title_str,
        description=str(description)[:10000] if description else None,
        location=_pick_job_location(posting),
        price=None,
        job_category=classify_job_category(None, title_str),
        employment_type=employment_type_from_text(posting.get("employmentType")),
        workload_min=workload_min,
        workload_max=workload_max,
        source_url=_pick_job_url(posting, base_url, default_detail_path, job_id),
        raw_payload={"source": source, "job_id": str(job_id), "parse": "json-ld"},
    )


def employment_type_from_text(raw: Any) -> EmploymentType | None:
    if raw is None:
        return None
    text = str(raw).casefold()
    if any(token in text for token in ("intern", "stage", "praktikum", "apprenti")):
        return EmploymentType.INTERNSHIP
    if any(token in text for token in ("temp", "cdd", "befrist", "temporaire")):
        return EmploymentType.TEMPORARY
    if any(token in text for token in ("freelance", "independent", "mandat")):
        return EmploymentType.FREELANCE
    if any(
        token in text
        for token in (
            "permanent",
            "cdi",
            "fest",
            "unbefrist",
            "indetermin",
            "indétermin",
            "dauer",
        )
    ):
        return EmploymentType.PERMANENT
    return EmploymentType.OTHER


def workload_from_title(title: str) -> tuple[int | None, int | None]:
    match = _WORKLOAD_RE.search(title)
    if not match:
        return None, None
    low = int(match.group(1))
    high = int(match.group(2)) if match.group(2) else low
    return low, high


def _pick_job_id(posting: dict[str, Any]) -> str | None:
    identifier = posting.get("identifier")
    if isinstance(identifier, dict):
        value = identifier.get("value")
        if value:
            return str(value)
    url = posting.get("url")
    if isinstance(url, str) and "/detail/" in url:
        tail = url.rstrip("/").split("/detail/", maxsplit=1)[-1]
        if tail:
            return tail.split("/", maxsplit=1)[0]
    return None


def _pick_hiring_organization(posting: dict[str, Any]) -> str | None:
    org = posting.get("hiringOrganization")
    if isinstance(org, dict):
        name = org.get("name")
        return str(name) if name else None
    if isinstance(org, str):
        return org
    return None


def _pick_job_location(posting: dict[str, Any]) -> str | None:
    location = posting.get("jobLocation")
    if isinstance(location, list):
        location = location[0] if location else None
    if not isinstance(location, dict):
        return str(location)[:200] if location else None
    address = location.get("address")
    if isinstance(address, dict):
        parts = [
            address.get("addressLocality"),
            address.get("addressRegion"),
            address.get("postalCode"),
        ]
        joined = ", ".join(str(part) for part in parts if part)
        if joined:
            return joined[:200]
    name = location.get("name")
    return str(name)[:200] if name else None


def _pick_job_url(
    posting: dict[str, Any],
    base_url: str,
    default_detail_path: str,
    job_id: str,
) -> str:
    url = posting.get("url")
    if isinstance(url, str) and url.startswith("http"):
        return url
    if isinstance(url, str) and url.startswith("/"):
        return f"{base_url}{url}"
    return f"{base_url}{default_detail_path.format(job_id=job_id)}"


def split_csv(raw: str) -> list[str]:
    ordered: list[str] = []
    for item in raw.split(","):
        value = item.strip()
        if value and value not in ordered:
            ordered.append(value)
    return ordered


def build_search_url(
    base_url: str,
    search_path: str,
    *,
    location: str | None = None,
    term: str | None = None,
    page: int = 1,
) -> str:
    params: dict[str, str] = {}
    if location:
        params["location"] = location
    if term:
        params["term"] = term
    if page > 1:
        params["page"] = str(page)
    if not params:
        return f"{base_url}{search_path}"
    return f"{base_url}{search_path}?{urlencode(params)}"


def iter_search_urls(
    settings: Settings,
    *,
    base_url: str,
    search_path: str,
    locations_csv: str,
    role_locations_csv: str,
) -> Iterator[str]:
    locations = split_csv(locations_csv)
    for location in locations:
        for page in range(1, settings.jobcloud_max_pages + 1):
            yield build_search_url(base_url, search_path, location=location, page=page)
    for location in split_csv(role_locations_csv):
        for term in split_csv(settings.jobcloud_role_keywords):
            yield build_search_url(base_url, search_path, location=location, term=term, page=1)


def fetch_jobcloud_listings(
    settings: Settings,
    *,
    source: str,
    base_url: str,
    search_path: str,
    state_markers: tuple[str, ...],
    parse_state: Callable[[dict[str, Any]], list[RawListing]],
    default_detail_path: str,
    locations_csv: str,
    role_locations_csv: str,
    search_url: str | None,
    provider_label: str,
    fetch_error: type[Exception],
) -> list[RawListing]:
    """Fetch and dedupe listings across cities, pages, and role-keyword passes."""
    if search_url:
        urls = [search_url]
    else:
        urls = list(
            iter_search_urls(
                settings,
                base_url=base_url,
                search_path=search_path,
                locations_csv=locations_csv,
                role_locations_csv=role_locations_csv,
            )
        )

    headers = {"User-Agent": settings.ingest_user_agent}
    seen: set[str] = set()
    parsed: list[RawListing] = []
    http_errors = 0

    for url in urls:
        try:
            time.sleep(settings.ingest_rate_limit_seconds)
            response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError:
            http_errors += 1
            continue

        try:
            batch = parse_jobcloud_search_html(
                response.text,
                source=source,
                base_url=base_url,
                state_markers=state_markers,
                parse_state=parse_state,
                default_detail_path=default_detail_path,
            )
        except EmbedParseError:
            continue

        for item in batch:
            if item.external_id in seen:
                continue
            seen.add(item.external_id)
            parsed.append(item)

    if http_errors == len(urls):
        msg = f"{provider_label} request failed for all {len(urls)} search URLs"
        raise fetch_error(msg)
    return parsed
