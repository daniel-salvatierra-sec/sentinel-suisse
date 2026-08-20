"""Richemont (luxury goods group) — Workday "Candidate Experience" JSON API, no scraping.

Richemont's public careers site (careers.richemont.com) is powered by Workday, and like
every Workday-hosted career site it is really a client-side app calling a public,
keyless JSON API underneath. The exact same API is used by the site's own React/JS UI to
render search results — reading it directly is not scraping, just skipping the HTML
shell. See docs/providers/richemont.md.

Richemont posts jobs globally across all its Maisons (Cartier, Van Cleef & Arpels, IWC,
Vacheron Constantin, Jaeger-LeCoultre, Buccellati, etc.), so unlike the other connectors
this one must filter a large multi-country result set down to Switzerland/France. The
Workday search API supports server-side filtering via `appliedFacets.locations`, but the
list-level results don't carry a country code — only the per-posting *detail* endpoint
does (`jobRequisitionLocation.country.alpha2Code`), which we already have to call to get
the full job description anyway. So the flow is: (1) fetch the "locations" facet once to
find candidate location IDs matching a curated list of known CH/FR place names, (2) page
through only those locations, (3) fetch each posting's detail and use its authoritative
country code as the final CH/FR filter (catches any accidental non-CH/FR matches from
step 1's substring heuristic).
"""

import html
import re
import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType

_WORKDAY_BASE = "https://richemont.wd3.myworkdayjobs.com"
_TENANT_SITE_PATH = "/wday/cxs/richemont/broadbean_external"
_SEARCH_URL = f"{_WORKDAY_BASE}{_TENANT_SITE_PATH}/jobs"
_DETAIL_BASE = f"{_WORKDAY_BASE}{_TENANT_SITE_PATH}"
# Workday's CXS API rejects page sizes above the site's configured default (confirmed:
# limit=50/100 -> HTTP 400, limit=20 -> OK — matches the "20 per page" the public UI uses).
_PAGE_LIMIT = 20

_COUNTRY_ALPHA2_MAP: dict[str, CountryCode] = {
    "CH": CountryCode.CH,
    "FR": CountryCode.FR,
}
_COUNTRY_DESCRIPTOR_MAP: dict[str, CountryCode] = {
    "switzerland": CountryCode.CH,
    "france": CountryCode.FR,
}

# Curated candidate location names (Richemont's Workday "locations" facet descriptors,
# upper-cased) used ONLY to narrow down which locations to page through — the final
# CH/FR decision always comes from the per-posting detail endpoint's authoritative
# country code, so a stray false-positive match here is harmless (just one wasted detail
# call), while a missing name here means a real CH/FR posting could be skipped. Update
# this list if Richemont opens a site in a city not covered below.
_LOCATION_HINTS: frozenset[str] = frozenset(
    {
        # Switzerland — manufacture/HQ sites concentrated in Geneva, the Jura watchmaking
        # arc and Neuchâtel, plus other major Swiss cities as a safety net.
        "GENEVA",
        "GENEVE",
        "GENÈVE",
        "MEYRIN",
        "PLAN-LES-OUATES",
        "CAROUGE",
        "VERNIER",
        "LE LOCLE",
        "LA CHAUX-DE-FONDS",
        "NEUCHATEL",
        "NEUCHÂTEL",
        "VILLARS SUR GLANE",
        "FRIBOURG",
        "LES BREULEUX",
        "LE SENTIER",
        "VILLERET",
        "SAINT-IMIER",
        "TRAMELAN",
        "MOUTIER",
        "BIENNE",
        "BIEL",
        "ZURICH",
        "ZÜRICH",
        "BASEL",
        "BALE",
        "BÂLE",
        "BERN",
        "BERNE",
        "LAUSANNE",
        "VEVEY",
        "MONTREUX",
        "ZUG",
        "LUGANO",
        "SWITZERLAND",
        "SUISSE",
        # France — Paris dominates (retail/HQ functions), plus resort boutiques and a
        # handful of manufacture/logistics sites.
        "PARIS",
        "LYON",
        "MARSEILLE",
        "NICE",
        "CANNES",
        "BIARRITZ",
        "BEAUNE",
        "BEZANNES",
        "SAINT DIE DES VOSGES",
        "BORDEAUX",
        "STRASBOURG",
        "LILLE",
        "NANTES",
        "TOULOUSE",
        "MONTPELLIER",
        "RENNES",
        "ANNEMASSE",
        "THONON",
        "ANNECY",
        "CHAMONIX",
        "DEAUVILLE",
        "COURCHEVEL",
        "MEGEVE",
        "FRANCE",
    }
)

_BLOCK_TAG_RE = re.compile(r"</(p|div|h[1-6]|li)>|<br\s*/?>", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"[ \t]+")


def _strip_html(raw: str) -> str:
    text = _BLOCK_TAG_RE.sub("\n", raw)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WHITESPACE_RE.sub(" ", text)
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line).strip()


class RichemontFetchError(RuntimeError):
    """Richemont Workday API HTTP or parse failure."""


class RichemontDisabledError(RuntimeError):
    """Live Richemont ingest is not enabled in settings."""


def _find_location_facet_values(facets: list[Any]) -> list[dict[str, Any]]:
    for facet in facets:
        if not isinstance(facet, dict):
            continue
        if facet.get("facetParameter") == "locations":
            values = facet.get("values")
            return values if isinstance(values, list) else []
        nested = facet.get("values")
        if isinstance(nested, list):
            found = _find_location_facet_values(nested)
            if found:
                return found
    return []


def _pick_employment_type(title: str) -> EmploymentType:
    lowered = title.lower()
    if "stage" in lowered or "intern" in lowered or "apprenti" in lowered:
        return EmploymentType.INTERNSHIP
    if (
        "cdd" in lowered
        or "fixed term" in lowered
        or "temporary" in lowered
        or "saisonnier" in lowered
        or "seasonal" in lowered
    ):
        return EmploymentType.TEMPORARY
    if "freelance" in lowered or "independent" in lowered:
        return EmploymentType.FREELANCE
    return EmploymentType.PERMANENT


def _pick_country(info: dict[str, Any]) -> CountryCode | None:
    req_location = info.get("jobRequisitionLocation")
    if isinstance(req_location, dict):
        country = req_location.get("country")
        if isinstance(country, dict):
            alpha2 = country.get("alpha2Code")
            if alpha2:
                mapped = _COUNTRY_ALPHA2_MAP.get(str(alpha2).upper())
                if mapped is not None:
                    return mapped
    country = info.get("country")
    if isinstance(country, dict):
        descriptor = str(country.get("descriptor", "")).lower()
        return _COUNTRY_DESCRIPTOR_MAP.get(descriptor)
    return None


def _fetch_detail(settings: Settings, external_path: str) -> dict[str, Any] | None:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(
            f"{_DETAIL_BASE}{external_path}",
            headers={"Accept": "application/json", "User-Agent": settings.ingest_user_agent},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        # Best-effort: a single failed detail call shouldn't fail the whole run, and we
        # can't build a valid listing without the authoritative country code anyway.
        return None


def _map_posting(list_item: dict[str, Any], settings: Settings) -> RawListing | None:
    external_path = list_item.get("externalPath")
    title = list_item.get("title")
    if not external_path or not title:
        return None

    detail = _fetch_detail(settings, str(external_path))
    if detail is None:
        return None

    info = detail.get("jobPostingInfo")
    if not isinstance(info, dict):
        return None

    country_code = _pick_country(info)
    if country_code is None:
        # Safety net for the location-name heuristic used to build the candidate list —
        # only CH/FR are supported by the app.
        return None

    job_req_id = info.get("jobReqId")
    if not job_req_id:
        return None

    raw_description = info.get("jobDescription")
    description = _strip_html(str(raw_description)) if raw_description else None

    city = info.get("location")
    location = str(city).title() if city else None

    source_url = info.get("externalUrl") or f"{_WORKDAY_BASE}{external_path}"

    hiring_org = detail.get("hiringOrganization")
    maison = hiring_org.get("name") if isinstance(hiring_org, dict) else None

    return RawListing(
        external_id=f"richemont-{job_req_id}",
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=description[:10000] if description else None,
        location=location[:200] if location else None,
        country=country_code,
        price=None,
        job_category=str(maison)[:80] if maison else None,
        employment_type=_pick_employment_type(str(title)),
        source_url=str(source_url),
        raw_payload={"source": "richemont", "job_req_id": str(job_req_id), "maison": maison},
    )


def parse_search_page(payload: dict[str, Any], settings: Settings) -> list[RawListing]:
    postings = payload.get("jobPostings")
    if not isinstance(postings, list):
        msg = "Unexpected Richemont search response shape (missing 'jobPostings')"
        raise RichemontFetchError(msg)

    parsed: list[RawListing] = []
    for item in postings:
        if not isinstance(item, dict):
            continue
        raw = _map_posting(item, settings)
        if raw is not None:
            parsed.append(raw)
    return parsed


def _post_search(
    settings: Settings, applied_facets: dict[str, Any], limit: int, offset: int
) -> dict[str, Any]:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.post(
            _SEARCH_URL,
            json={
                "appliedFacets": applied_facets,
                "limit": limit,
                "offset": offset,
                "searchText": "",
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": settings.ingest_user_agent,
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"Richemont Workday search request failed: {exc}"
        raise RichemontFetchError(msg) from exc

    try:
        return response.json()
    except ValueError as exc:
        msg = f"Richemont Workday search response was not valid JSON: {exc}"
        raise RichemontFetchError(msg) from exc


def pick_candidate_location_ids(payload: dict[str, Any], settings: Settings) -> list[str]:
    facets = payload.get("facets")
    if not isinstance(facets, list):
        msg = "Unexpected Richemont facets response shape (missing 'facets')"
        raise RichemontFetchError(msg)

    location_values = _find_location_facet_values(facets)
    extra_hints = {
        hint.strip().upper()
        for hint in settings.richemont_extra_location_hints.split(",")
        if hint.strip()
    }
    hints = _LOCATION_HINTS | extra_hints

    ids: list[str] = []
    for entry in location_values:
        if not isinstance(entry, dict):
            continue
        descriptor = str(entry.get("descriptor", "")).upper()
        if any(hint in descriptor for hint in hints):
            loc_id = entry.get("id")
            if loc_id:
                ids.append(str(loc_id))
    return ids


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query the official Richemont Workday CXS API. `search_url` is unused — kept only
    to match the other connectors' `fetch_search_listings(settings, search_url)`
    signature used by the ingest CLI."""
    if not settings.ingest_richemont_live:
        msg = "Live Richemont ingest is disabled (set INGEST_RICHEMONT_LIVE=true)"
        raise RichemontDisabledError(msg)

    facets_payload = _post_search(settings, applied_facets={}, limit=1, offset=0)
    location_ids = pick_candidate_location_ids(facets_payload, settings)
    if not location_ids:
        return []

    all_items: list[RawListing] = []
    offset = 0
    while True:
        payload = _post_search(
            settings,
            applied_facets={"locations": location_ids},
            limit=_PAGE_LIMIT,
            offset=offset,
        )
        all_items.extend(parse_search_page(payload, settings))

        total_found = payload.get("total", 0)
        offset += _PAGE_LIMIT
        if offset >= total_found:
            break

    return all_items
