"""Adzuna job search API — official, self-serve, built for redistribution. Not scraping.

Adzuna is a job-board aggregator that explicitly documents this exact use case:
"Get job ads to display on your own website" (developer.adzuna.com). Free registration
gives an app_id/app_key pair — see docs/providers/adzuna.md. Covers both Switzerland
(country code "ch") and France ("fr"), so this single connector can be reused for both.
"""

import time
from decimal import Decimal
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType

_SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"

_COUNTRY_MAP: dict[str, CountryCode] = {
    "ch": CountryCode.CH,
    "fr": CountryCode.FR,
}

_CONTRACT_TYPE_MAP: dict[str, EmploymentType] = {
    "permanent": EmploymentType.PERMANENT,
    "contract": EmploymentType.TEMPORARY,
}


class AdzunaFetchError(RuntimeError):
    """Adzuna API HTTP or parse failure."""


class AdzunaDisabledError(RuntimeError):
    """Live Adzuna ingest is not enabled in settings."""


def _pick_employment_type(
    contract_type: str | None, contract_time: str | None
) -> EmploymentType | None:
    if contract_type:
        mapped = _CONTRACT_TYPE_MAP.get(contract_type.lower())
        if mapped is not None:
            return mapped
    if contract_time:
        return EmploymentType.OTHER
    return None


def _map_job(job: dict[str, Any], country: CountryCode) -> RawListing | None:
    job_id = job.get("id")
    title = job.get("title")
    url = job.get("redirect_url")
    if not job_id or not title or not url:
        return None

    location = job.get("location")
    display_name = location.get("display_name") if isinstance(location, dict) else None

    company = job.get("company")
    company_name = company.get("display_name") if isinstance(company, dict) else None

    salary_min = job.get("salary_min")
    price = (
        Decimal(str(salary_min)) if isinstance(salary_min, int | float) and salary_min > 0 else None
    )

    category = job.get("category")
    category_label = category.get("label") if isinstance(category, dict) else None

    return RawListing(
        external_id=str(job_id),
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=str(job.get("description"))[:10000] if job.get("description") else None,
        location=str(display_name)[:200] if display_name else None,
        country=country,
        price=price,
        job_category=str(category_label)[:80] if category_label else None,
        employment_type=_pick_employment_type(job.get("contract_type"), job.get("contract_time")),
        source_url=str(url),
        raw_payload={"source": "adzuna", "job_id": str(job_id), "company": company_name},
    )


def parse_search_response(payload: dict[str, Any], country: CountryCode) -> list[RawListing]:
    results = payload.get("results")
    if not isinstance(results, list):
        msg = "Unexpected Adzuna search response shape (missing 'results')"
        raise AdzunaFetchError(msg)

    parsed: list[RawListing] = []
    for job in results:
        if not isinstance(job, dict):
            continue
        raw = _map_job(job, country)
        if raw is not None:
            parsed.append(raw)
    return parsed


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query the official Adzuna job search API. `search_url` is unused — kept only to match
    the other connectors' `fetch_search_listings(settings, search_url)` signature used by the
    ingest CLI."""
    if not settings.ingest_adzuna_live:
        msg = "Live Adzuna ingest is disabled (set INGEST_ADZUNA_LIVE=true)"
        raise AdzunaDisabledError(msg)
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        msg = "ADZUNA_APP_ID / ADZUNA_APP_KEY are not set — register a free key at https://developer.adzuna.com/signup"
        raise AdzunaFetchError(msg)

    country_code = settings.adzuna_country.lower()
    country = _COUNTRY_MAP.get(country_code, CountryCode.CH)
    url = _SEARCH_URL.format(country=country_code)

    params: dict[str, str] = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": "50",
        "content-type": "application/json",
    }
    if settings.adzuna_keywords:
        params["what"] = settings.adzuna_keywords
    if settings.adzuna_location:
        params["where"] = settings.adzuna_location

    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(
            url,
            params=params,
            headers={"User-Agent": settings.ingest_user_agent},
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"Adzuna search request failed: {exc}"
        raise AdzunaFetchError(msg) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        msg = f"Adzuna search response was not valid JSON: {exc}"
        raise AdzunaFetchError(msg) from exc

    return parse_search_response(payload, country)
