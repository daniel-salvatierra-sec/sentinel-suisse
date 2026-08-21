"""Adzuna job search API — official, self-serve, built for redistribution. Not scraping.

Adzuna is a job-board aggregator that explicitly documents this exact use case:
"Get job ads to display on your own website" (developer.adzuna.com). Free registration
gives an app_id/app_key pair — see docs/providers/adzuna.md. Covers both Switzerland
(country code "ch") and France ("fr"), so this single connector can be reused for both.
"""

import re
import time
from decimal import Decimal
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType
from sentinel_suisse.services.job_taxonomy import classify_job_category

_SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
_PAGE_SIZE = 50

_COUNTRY_MAP: dict[str, CountryCode] = {
    "ch": CountryCode.CH,
    "fr": CountryCode.FR,
}

_CONTRACT_TYPE_MAP: dict[str, EmploymentType] = {
    "permanent": EmploymentType.PERMANENT,
    "contract": EmploymentType.TEMPORARY,
}

# Adzuna's Swiss location names come back in German (e.g. "Genf", "Kanton Genf,
# Schweiz") regardless of query language. The rest of the app (jobs.ch, jobup,
# Homegate, etc. fixtures) consistently uses English "Geneva" for search matching
# (services/search.py does a plain ILIKE substring match, no cross-language lookup),
# so normalize known Swiss canton/city names here to keep listings findable and avoid
# mixing German scaffolding words ("Kanton", "Schweiz") with the translated name.
_LOCATION_TRANSLATIONS: dict[str, str] = {
    "Genf": "Geneva",
    "Zürich": "Zurich",
    "Basel-Stadt": "Basel",
    "Waadt": "Vaud",
}

# "Kanton Genf, Schweiz" (canton-level only, no specific city known) -> just "Geneva".
_CANTON_ONLY_RE = re.compile(r"^Kanton (?P<canton>[\w\s\-]+), Schweiz$")


def _translate_location(display_name: str) -> str:
    canton_match = _CANTON_ONLY_RE.match(display_name)
    if canton_match:
        canton = canton_match.group("canton")
        return _LOCATION_TRANSLATIONS.get(canton, canton)

    translated = display_name
    for german, english in _LOCATION_TRANSLATIONS.items():
        translated = translated.replace(german, english)
    # Drop a leftover trailing ", Schweiz" for any other pattern we didn't anticipate,
    # rather than shipping a name that's half-translated.
    return re.sub(r",?\s*Schweiz$", "", translated).strip()


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
    if display_name:
        display_name = _translate_location(str(display_name))

    company = job.get("company")
    company_name = company.get("display_name") if isinstance(company, dict) else None

    salary_min = job.get("salary_min")
    price = (
        Decimal(str(salary_min)) if isinstance(salary_min, int | float) and salary_min > 0 else None
    )

    category = job.get("category")
    category_tag = category.get("tag") if isinstance(category, dict) else None
    category_label = category.get("label") if isinstance(category, dict) else None
    raw_category = str(category_tag or category_label) if (category_tag or category_label) else None

    return RawListing(
        external_id=str(job_id),
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=str(job.get("description"))[:10000] if job.get("description") else None,
        location=str(display_name)[:200] if display_name else None,
        country=country,
        price=price,
        job_category=classify_job_category(raw_category, str(title)),
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
    parsed: list[RawListing] = []
    seen: set[str] = set()
    max_pages = max(1, settings.adzuna_max_pages)
    page_size = str(_PAGE_SIZE)

    for page in range(1, max_pages + 1):
        url = _SEARCH_URL.format(country=country_code, page=page)
        params: dict[str, str] = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "results_per_page": page_size,
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

        batch = parse_search_response(payload, country)
        for item in batch:
            if item.external_id in seen:
                continue
            seen.add(item.external_id)
            parsed.append(item)
        if len(batch) < _PAGE_SIZE:
            break

    return parsed
