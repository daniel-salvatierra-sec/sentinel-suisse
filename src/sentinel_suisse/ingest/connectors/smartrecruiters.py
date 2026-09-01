"""SmartRecruiters public Postings API — official, keyless, built for job-board syndication.

SmartRecruiters explicitly publishes this API for exactly this use case: any company's
public postings can be read with no authentication via
`api.smartrecruiters.com/v1/companies/{id}/postings`. This is the same data that powers
SmartRecruiters' own `jobs.smartrecruiters.com/<company>` career pages, and is routinely
consumed by external job boards/aggregators. Not scraping — see
docs/providers/smartrecruiters.md.

Geneva-area employers on this API include HUG, CERN, IMAD, Hospice Général, and SGS
(SGS is global — we only pull CH/FR/DE/IT). Configure SMARTRECRUITERS_COMPANIES as a
comma-separated list of company identifiers — the token that appears in their
careers.smartrecruiters.com/<identifier> URL.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType
from sentinel_suisse.services.job_taxonomy import canonical_job_category

logger = logging.getLogger(__name__)

_POSTINGS_URL = "https://api.smartrecruiters.com/v1/companies/{company}/postings"
_POSTING_DETAIL_URL = "https://api.smartrecruiters.com/v1/companies/{company}/postings/{posting_id}"
_PAGE_LIMIT = 100
_COUNTRY_QUERY = ("ch", "fr", "de", "it")

_COUNTRY_MAP: dict[str, CountryCode] = {
    "ch": CountryCode.CH,
    "fr": CountryCode.FR,
    "de": CountryCode.DE,
    "it": CountryCode.IT,
}

_EMPLOYMENT_TYPE_MAP: dict[str, EmploymentType] = {
    "permanent": EmploymentType.PERMANENT,
    "temporary": EmploymentType.TEMPORARY,
    "intern": EmploymentType.INTERNSHIP,
    "internship": EmploymentType.INTERNSHIP,
    "contract": EmploymentType.TEMPORARY,
    "freelance": EmploymentType.FREELANCE,
    "per_diem": EmploymentType.OTHER,
    "seasonal": EmploymentType.TEMPORARY,
}

# SmartRecruiters returns Swiss Romande/German locations in French or German ("Genève",
# "Zürich") — the rest of the app (jobup, jobs.ch fixtures) consistently uses English city
# names for search matching (services/search.py does a plain ILIKE substring match, no
# cross-language lookup), so normalize the handful of names that actually differ.
_LOCATION_TRANSLATIONS: dict[str, str] = {
    "Genève": "Geneva",
    "Geneve": "Geneva",
    "Genf": "Geneva",
    "Zürich": "Zurich",
    "Zurich": "Zurich",
    "Bâle": "Basel",
    "Basel": "Basel",
    "Berne": "Bern",
    "Bern": "Bern",
}


def _translate_location(city: str) -> str:
    return _LOCATION_TRANSLATIONS.get(city, city)


class SmartRecruitersFetchError(RuntimeError):
    """SmartRecruiters API HTTP or parse failure."""


class SmartRecruitersDisabledError(RuntimeError):
    """Live SmartRecruiters ingest is not enabled in settings."""


def _pick_employment_type(type_of_employment: Any) -> EmploymentType | None:
    if not isinstance(type_of_employment, dict):
        return None
    type_id = type_of_employment.get("id")
    if not type_id:
        return None
    return _EMPLOYMENT_TYPE_MAP.get(str(type_id).lower(), EmploymentType.OTHER)


def _extract_description(detail: dict[str, Any]) -> str | None:
    job_ad = detail.get("jobAd")
    if not isinstance(job_ad, dict):
        return None
    sections = job_ad.get("sections")
    if not isinstance(sections, dict):
        return None
    parts: list[str] = []
    for key in ("jobDescription", "qualifications", "additionalInformation"):
        section = sections.get(key)
        if isinstance(section, dict):
            text = section.get("text")
            if text:
                parts.append(str(text).strip())
    return "\n\n".join(parts) if parts else None


def _fetch_posting_detail(
    settings: Settings, company: str, posting_id: str
) -> dict[str, Any] | None:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(
            _POSTING_DETAIL_URL.format(company=company, posting_id=posting_id),
            headers={"User-Agent": settings.ingest_user_agent},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        # Best-effort enrichment — fall back to the list-level fields if the detail
        # call fails (rate limit, transient error, unpublished posting, etc.).
        return None


def _map_posting(posting: dict[str, Any], settings: Settings, company: str) -> RawListing | None:
    posting_id = posting.get("id")
    title = posting.get("name")
    if not posting_id or not title:
        return None

    location = posting.get("location")
    country_code = None
    city = None
    if isinstance(location, dict):
        country_code = _COUNTRY_MAP.get(str(location.get("country", "")).lower())
        city = location.get("city")
    if country_code is None:
        return None

    industry = posting.get("industry")
    industry_label = industry.get("label") if isinstance(industry, dict) else None

    source_url = f"https://jobs.smartrecruiters.com/{company}/{posting_id}"
    description = None
    if settings.smartrecruiters_fetch_details:
        detail = _fetch_posting_detail(settings, company, str(posting_id))
        if detail:
            description = _extract_description(detail)
            apply_url = detail.get("postingUrl") or detail.get("applyUrl")
            if apply_url:
                source_url = str(apply_url)

    return RawListing(
        external_id=f"{company}-{posting_id}",
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=description[:10000] if description else None,
        location=_translate_location(str(city))[:200] if city else None,
        country=country_code,
        price=None,
        job_category=canonical_job_category(str(industry_label) if industry_label else None),
        employment_type=_pick_employment_type(posting.get("typeOfEmployment")),
        source_url=source_url,
        raw_payload={
            "source": "smartrecruiters",
            "company": company,
            "posting_id": str(posting_id),
        },
    )


def parse_postings_response(
    payload: dict[str, Any], settings: Settings, company: str
) -> list[RawListing]:
    content = payload.get("content")
    if not isinstance(content, list):
        msg = "Unexpected SmartRecruiters postings response shape (missing 'content')"
        raise SmartRecruitersFetchError(msg)

    parsed: list[RawListing] = []
    for posting in content:
        if not isinstance(posting, dict):
            continue
        raw = _map_posting(posting, settings, company)
        if raw is not None:
            parsed.append(raw)
    return parsed


def _fetch_company_country(settings: Settings, company: str, country: str) -> list[RawListing]:
    all_items: list[RawListing] = []
    offset = 0
    while True:
        try:
            time.sleep(settings.ingest_rate_limit_seconds)
            response = httpx.get(
                _POSTINGS_URL.format(company=company),
                params={"limit": _PAGE_LIMIT, "offset": offset, "country": country},
                headers={"User-Agent": settings.ingest_user_agent},
                timeout=30.0,
            )
            if response.status_code in {403, 404}:
                logger.warning(
                    "smartrecruiters skip company=%s country=%s status=%s",
                    company,
                    country,
                    response.status_code,
                )
                return []
            response.raise_for_status()
        except httpx.HTTPError as exc:
            msg = (
                f"SmartRecruiters postings request failed for company={company!r} "
                f"country={country!r}: {exc}"
            )
            raise SmartRecruitersFetchError(msg) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            msg = (
                f"SmartRecruiters postings response was not valid JSON for "
                f"company={company!r} country={country!r}: {exc}"
            )
            raise SmartRecruitersFetchError(msg) from exc

        all_items.extend(parse_postings_response(payload, settings, company))

        total_found = payload.get("totalFound", 0)
        offset += _PAGE_LIMIT
        if offset >= total_found:
            break

    return all_items


def _fetch_company_postings(settings: Settings, company: str) -> list[RawListing]:
    all_items: list[RawListing] = []
    for country in _COUNTRY_QUERY:
        all_items.extend(_fetch_company_country(settings, company, country))
    return all_items


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query the official SmartRecruiters Postings API for each configured company.
    `search_url` is unused — kept only to match the other connectors'
    `fetch_search_listings(settings, search_url)` signature used by the ingest CLI."""
    if not settings.ingest_smartrecruiters_live:
        msg = "Live SmartRecruiters ingest is disabled (set INGEST_SMARTRECRUITERS_LIVE=true)"
        raise SmartRecruitersDisabledError(msg)

    companies = [c.strip() for c in settings.smartrecruiters_companies.split(",") if c.strip()]
    if not companies:
        msg = "SMARTRECRUITERS_COMPANIES is empty — set at least one company identifier"
        raise SmartRecruitersFetchError(msg)

    all_items: list[RawListing] = []
    for company in companies:
        all_items.extend(_fetch_company_postings(settings, company))
    return all_items
