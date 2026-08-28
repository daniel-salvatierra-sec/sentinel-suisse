"""Shared parsing for JobCloud portals (jobup.ch, jobs.ch)."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

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
