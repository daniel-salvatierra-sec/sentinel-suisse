"""Extract job vacancies from Indeed France search page embedded JSON."""

import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import EmbedParseError, extract_first_state
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType

_INDEED_BASE = "https://fr.indeed.com"
_STATE_MARKERS = (
    "window.__NEXT_DATA__=",
    "window.__INITIAL_DATA__=",
    "window._initialData=",
)

_VACANCY_PATHS: tuple[tuple[str, ...], ...] = (
    ("props", "pageProps", "jobList"),
    ("props", "pageProps", "results"),
    ("jobList",),
    ("results",),
    ("jobs",),
    ("search", "results"),
)


class IndeedFrFetchError(RuntimeError):
    """Indeed FR HTTP or parse failure."""


class IndeedFrDisabledError(RuntimeError):
    """Live Indeed FR ingest is not enabled in settings."""


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    vacancies = _find_vacancies(state)
    if vacancies is None:
        msg = "Unexpected Indeed FR search state shape"
        raise IndeedFrFetchError(msg)

    parsed: list[RawListing] = []
    for vacancy in vacancies:
        if not isinstance(vacancy, dict):
            continue
        raw = _map_vacancy(vacancy)
        if raw is not None:
            parsed.append(raw)
    return parsed


def _find_vacancies(state: dict[str, Any]) -> list[Any] | None:
    for path in _VACANCY_PATHS:
        node: Any = state
        for key in path:
            if not isinstance(node, dict):
                node = None
                break
            node = node.get(key)
        if isinstance(node, list):
            return node
    return None


def _map_vacancy(vacancy: dict[str, Any]) -> RawListing | None:
    job_id = (
        vacancy.get("jobkey") or vacancy.get("jobKey") or vacancy.get("id") or vacancy.get("jk")
    )
    title = vacancy.get("title") or vacancy.get("jobTitle") or vacancy.get("normalizedTitle")
    if job_id is None or not title:
        return None

    company = _pick_company(vacancy)
    description = vacancy.get("snippet") or vacancy.get("description")
    if description is None and company:
        description = company

    location = (
        vacancy.get("formattedLocation") or vacancy.get("jobLocation") or vacancy.get("location")
    )
    if isinstance(location, dict):
        location = location.get("formatted") or location.get("city")

    return RawListing(
        external_id=str(job_id),
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=str(description)[:10000] if description else None,
        location=str(location)[:200] if location else None,
        country=CountryCode.FR,
        price=None,
        job_category=_pick_job_category(vacancy),
        employment_type=_pick_employment_type(vacancy),
        workload_min=_pick_workload(vacancy, "min"),
        workload_max=_pick_workload(vacancy, "max"),
        source_url=_pick_source_url(vacancy, job_id),
        raw_payload={"source": "indeed_fr", "job_id": str(job_id)},
    )


def _pick_company(vacancy: dict[str, Any]) -> str | None:
    company = vacancy.get("company") or vacancy.get("companyName")
    if isinstance(company, dict):
        name = company.get("name")
        return str(name) if name else None
    if isinstance(company, str):
        return company
    return None


def _pick_job_category(vacancy: dict[str, Any]) -> str | None:
    for key in ("jobCategory", "taxonomy", "occupation", "category"):
        value = vacancy.get(key)
        if isinstance(value, dict):
            name = value.get("slug") or value.get("name")
            if name:
                return str(name)[:80]
        if value and not isinstance(value, list):
            return str(value)[:80]
    return None


def _pick_employment_type(vacancy: dict[str, Any]) -> EmploymentType | None:
    raw = vacancy.get("jobTypes") or vacancy.get("employmentType") or vacancy.get("jobType")
    if isinstance(raw, list) and raw:
        raw = raw[0]
    if raw is None:
        return None
    text = str(raw).lower()
    if "intern" in text or "stage" in text:
        return EmploymentType.INTERNSHIP
    if "temp" in text or "cdd" in text or "intérim" in text or "interim" in text:
        return EmploymentType.TEMPORARY
    if "freelance" in text or "independent" in text:
        return EmploymentType.FREELANCE
    if "permanent" in text or "cdi" in text or "full-time" in text or "temps plein" in text:
        return EmploymentType.PERMANENT
    return EmploymentType.OTHER


def _pick_workload(vacancy: dict[str, Any], bound: str) -> int | None:
    if bound == "min":
        keys = ("workloadMin", "hoursMin")
    else:
        keys = ("workloadMax", "hoursMax")
    for key in keys:
        value = vacancy.get(key)
        if value is not None:
            return int(value)
    return None


def _pick_source_url(vacancy: dict[str, Any], job_id: Any) -> str:
    for key in ("viewJobLink", "url", "link", "jobUrl"):
        value = vacancy.get(key)
        if value:
            url = str(value)
            if url.startswith("http"):
                return url
            return f"{_INDEED_BASE}{url}"
    return f"{_INDEED_BASE}/viewjob?jk={job_id}"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_indeed_fr_live:
        msg = "Live Indeed FR ingest is disabled (set INGEST_INDEED_FR_LIVE=true)"
        raise IndeedFrDisabledError(msg)

    url = search_url or settings.indeed_fr_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"Indeed FR request failed: {exc}"
        raise IndeedFrFetchError(msg) from exc

    try:
        state = extract_first_state(response.text, _STATE_MARKERS)
    except EmbedParseError as exc:
        msg = f"Indeed FR embedded state parse failed: {exc}"
        raise IndeedFrFetchError(msg) from exc

    return parse_search_state(state)
