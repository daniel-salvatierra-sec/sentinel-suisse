"""Extract job vacancies from jobup.ch search page embedded JSON."""

import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import EmbedParseError, extract_first_state
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import EmploymentType, ListingType

_JOBUP_BASE = "https://www.jobup.ch"
_STATE_MARKERS = (
    "window.__NEXT_DATA__=",
    "window.__INITIAL_STATE__=",
    "window.__NUXT__=",
)

_VACANCY_PATHS: tuple[tuple[str, ...], ...] = (
    ("props", "pageProps", "searchResult", "vacancies"),
    ("props", "pageProps", "jobs"),
    ("search", "vacancies"),
    ("search", "jobs"),
    ("vacancies",),
    ("jobs",),
)


class JobupFetchError(RuntimeError):
    """jobup.ch HTTP or parse failure."""


class JobupDisabledError(RuntimeError):
    """Live jobup.ch ingest is not enabled in settings."""


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    vacancies = _find_vacancies(state)
    if vacancies is None:
        msg = "Unexpected jobup.ch search state shape"
        raise JobupFetchError(msg)

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
    job_id = vacancy.get("id") or vacancy.get("jobId") or vacancy.get("vacancyId")
    title = vacancy.get("title") or vacancy.get("jobTitle") or vacancy.get("name")
    if job_id is None or not title:
        return None

    company = _pick_company(vacancy)
    description = vacancy.get("description")
    if description is None and company:
        description = f"{company}"

    location = vacancy.get("place") or vacancy.get("location") or vacancy.get("city")
    if isinstance(location, dict):
        location = location.get("name") or location.get("city")

    return RawListing(
        external_id=str(job_id),
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=str(description)[:10000] if description else None,
        location=str(location)[:200] if location else None,
        price=None,
        job_category=_pick_job_category(vacancy),
        employment_type=_pick_employment_type(vacancy),
        workload_min=_pick_workload(vacancy, "min"),
        workload_max=_pick_workload(vacancy, "max"),
        source_url=_pick_source_url(vacancy, job_id),
        raw_payload={"source": "jobup", "job_id": str(job_id)},
    )


def _pick_company(vacancy: dict[str, Any]) -> str | None:
    company = vacancy.get("company")
    if isinstance(company, dict):
        name = company.get("name")
        return str(name) if name else None
    if isinstance(company, str):
        return company
    return None


def _pick_job_category(vacancy: dict[str, Any]) -> str | None:
    for key in ("category", "jobCategory", "occupationalField", "field"):
        value = vacancy.get(key)
        if isinstance(value, dict):
            name = value.get("slug") or value.get("name")
            if name:
                return str(name)[:80]
        if value:
            return str(value)[:80]
    return None


def _pick_employment_type(vacancy: dict[str, Any]) -> EmploymentType | None:
    raw = vacancy.get("employmentType") or vacancy.get("contractType") or vacancy.get("jobType")
    if raw is None:
        return None
    text = str(raw).lower()
    if "intern" in text or "stage" in text or "praktikum" in text:
        return EmploymentType.INTERNSHIP
    if "temp" in text or "cdd" in text or "befrist" in text:
        return EmploymentType.TEMPORARY
    if "freelance" in text or "independent" in text:
        return EmploymentType.FREELANCE
    if "permanent" in text or "cdi" in text or "fest" in text or "unbefrist" in text:
        return EmploymentType.PERMANENT
    return EmploymentType.OTHER


def _pick_workload(vacancy: dict[str, Any], bound: str) -> int | None:
    if bound == "min":
        keys = ("workloadMin", "employmentGradeMin", "pensumMin", "workload_min")
    else:
        keys = ("workloadMax", "employmentGradeMax", "pensumMax", "workload_max")
    for key in keys:
        value = vacancy.get(key)
        if value is not None:
            return int(value)
    workload = vacancy.get("workload") or vacancy.get("pensum")
    if isinstance(workload, dict):
        value = workload.get(bound) or workload.get("from" if bound == "min" else "to")
        if value is not None:
            return int(value)
    if isinstance(workload, int | float) and bound == "min":
        return int(workload)
    if isinstance(workload, int | float) and bound == "max":
        return int(workload)
    return None


def _pick_source_url(vacancy: dict[str, Any], job_id: Any) -> str:
    for key in ("url", "jobUrl", "detailUrl", "link"):
        value = vacancy.get(key)
        if value:
            url = str(value)
            if url.startswith("http"):
                return url
            return f"{_JOBUP_BASE}{url}"
    return f"{_JOBUP_BASE}/fr/emplois/detail/{job_id}/"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_jobup_live:
        msg = "Live jobup.ch ingest is disabled (set INGEST_JOBUP_LIVE=true)"
        raise JobupDisabledError(msg)

    url = search_url or settings.jobup_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"jobup.ch request failed: {exc}"
        raise JobupFetchError(msg) from exc

    try:
        state = extract_first_state(response.text, _STATE_MARKERS)
    except EmbedParseError as exc:
        msg = f"jobup.ch embedded state parse failed: {exc}"
        raise JobupFetchError(msg) from exc

    return parse_search_state(state)
