"""Extract job vacancies from jobs.ch search page embedded JSON."""

import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import EmbedParseError, extract_first_state
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import ListingType

_JOBS_BASE = "https://www.jobs.ch"
_STATE_MARKERS = (
    "window.__NEXT_DATA__=",
    "window.__INITIAL_STATE__=",
    "window.__PINIA_INITIAL_STATE__=",
)

_VACANCY_PATHS: tuple[tuple[str, ...], ...] = (
    ("props", "pageProps", "searchResult", "vacancies"),
    ("props", "pageProps", "initialState", "search", "vacancies"),
    ("resultList", "search", "fullSearch", "result", "vacancies"),
    ("search", "result", "vacancies"),
    ("search", "vacancies"),
    ("vacancies",),
)


class JobsFetchError(RuntimeError):
    """jobs.ch HTTP or parse failure."""


class JobsDisabledError(RuntimeError):
    """Live jobs.ch ingest is not enabled in settings."""


def parse_search_state(state: dict[str, Any]) -> list[RawListing]:
    vacancies = _find_vacancies(state)
    if vacancies is None:
        msg = "Unexpected jobs.ch search state shape"
        raise JobsFetchError(msg)

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
    job_id = vacancy.get("id") or vacancy.get("jobId")
    title = vacancy.get("title") or vacancy.get("jobTitle")
    if job_id is None or not title:
        return None

    company = _pick_company(vacancy)
    description = vacancy.get("description")
    if description is None and company:
        description = f"{company}"

    location = vacancy.get("place") or vacancy.get("location")
    if location is None:
        location_obj = vacancy.get("location")
        if isinstance(location_obj, dict):
            location = location_obj.get("name") or location_obj.get("city")

    return RawListing(
        external_id=str(job_id),
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=str(description)[:10000] if description else None,
        location=str(location)[:200] if location else None,
        price=None,
        source_url=_pick_source_url(vacancy, job_id),
        raw_payload={"source": "jobs", "job_id": str(job_id)},
    )


def _pick_company(vacancy: dict[str, Any]) -> str | None:
    company = vacancy.get("company")
    if isinstance(company, dict):
        name = company.get("name")
        return str(name) if name else None
    if isinstance(company, str):
        return company
    return vacancy.get("company_name") if vacancy.get("company_name") else None


def _pick_source_url(vacancy: dict[str, Any], job_id: Any) -> str:
    for key in ("url", "jobUrl", "link_to_offer", "detailUrl"):
        value = vacancy.get(key)
        if value:
            url = str(value)
            if url.startswith("http"):
                return url
            return f"{_JOBS_BASE}{url}"
    return f"{_JOBS_BASE}/en/vacancies/detail/{job_id}/"


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    if not settings.ingest_jobs_live:
        msg = "Live jobs.ch ingest is disabled (set INGEST_JOBS_LIVE=true)"
        raise JobsDisabledError(msg)

    url = search_url or settings.jobs_search_url
    headers = {"User-Agent": settings.ingest_user_agent}
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"jobs.ch request failed: {exc}"
        raise JobsFetchError(msg) from exc

    try:
        state = extract_first_state(response.text, _STATE_MARKERS)
    except EmbedParseError as exc:
        msg = f"jobs.ch embedded state parse failed: {exc}"
        raise JobsFetchError(msg) from exc

    return parse_search_state(state)
