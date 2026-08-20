"""Shared Workday "Candidate Experience" (CXS) JSON client — no scraping.

Every Workday-hosted career site is a client-side app calling a public, keyless JSON
API. Reading it directly is what the site's own JavaScript does, minus the HTML shell.

Used by the Richemont, Lombard Odier, Logitech, P&G, and Temenos connectors.
Tenant/shard/site come from each employer's public career URL:

    https://{tenant}.{shard}.myworkdayjobs.com/{locale}/{site}

→ POST https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
"""

from __future__ import annotations

import html
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType

# Workday's CXS API rejects page sizes above the tenant's configured default
# (Richemont: limit=50/100 -> HTTP 400, limit=20 -> OK).
PAGE_LIMIT = 20

_COUNTRY_ALPHA2_MAP: dict[str, CountryCode] = {
    "CH": CountryCode.CH,
    "FR": CountryCode.FR,
}
_COUNTRY_DESCRIPTOR_MAP: dict[str, CountryCode] = {
    "switzerland": CountryCode.CH,
    "france": CountryCode.FR,
}

# Curated CH/FR place names used ONLY to narrow which locations to page through.
# Final country comes from the per-posting detail endpoint's alpha2Code.
LOCATION_HINTS: frozenset[str] = frozenset(
    {
        "GENEVA",
        "GENEVE",
        "GENÈVE",
        "GINEBRA",
        "MEYRIN",
        "PLAN-LES-OUATES",
        "CAROUGE",
        "LANCY",
        "PETIT-LANCY",
        "SCHLIEREN",
        "VERNIER",
        "BELLEVUE",
        "NYON",
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


@dataclass(frozen=True)
class WorkdaySite:
    """One employer's public Workday career site."""

    slug: str
    tenant: str
    shard: str
    site: str

    @property
    def base_url(self) -> str:
        return f"https://{self.tenant}.{self.shard}.myworkdayjobs.com"

    @property
    def cxs_path(self) -> str:
        return f"/wday/cxs/{self.tenant}/{self.site}"

    @property
    def search_url(self) -> str:
        return f"{self.base_url}{self.cxs_path}/jobs"

    @property
    def detail_base(self) -> str:
        return f"{self.base_url}{self.cxs_path}"


class WorkdayFetchError(RuntimeError):
    """Workday CXS API HTTP or parse failure."""


def strip_html(raw: str) -> str:
    text = _BLOCK_TAG_RE.sub("\n", raw)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WHITESPACE_RE.sub(" ", text)
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line).strip()


def pick_employment_type(title: str) -> EmploymentType:
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


def pick_country(info: dict[str, Any]) -> CountryCode | None:
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


def _fetch_detail(
    settings: Settings, workday_site: WorkdaySite, external_path: str
) -> dict[str, Any] | None:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.get(
            f"{workday_site.detail_base}{external_path}",
            headers={"Accept": "application/json", "User-Agent": settings.ingest_user_agent},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        return None


def map_posting(
    list_item: dict[str, Any], settings: Settings, workday_site: WorkdaySite
) -> RawListing | None:
    external_path = list_item.get("externalPath")
    title = list_item.get("title")
    if not external_path or not title:
        return None

    detail = _fetch_detail(settings, workday_site, str(external_path))
    if detail is None:
        return None

    info = detail.get("jobPostingInfo")
    if not isinstance(info, dict):
        return None

    country_code = pick_country(info)
    if country_code is None:
        return None

    job_req_id = info.get("jobReqId")
    if not job_req_id:
        return None

    raw_description = info.get("jobDescription")
    description = strip_html(str(raw_description)) if raw_description else None

    city = info.get("location")
    location = str(city).title() if city else None

    source_url = info.get("externalUrl") or f"{workday_site.base_url}{external_path}"

    hiring_org = detail.get("hiringOrganization")
    org_name = hiring_org.get("name") if isinstance(hiring_org, dict) else None

    return RawListing(
        external_id=f"{workday_site.slug}-{job_req_id}",
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=description[:10000] if description else None,
        location=location[:200] if location else None,
        country=country_code,
        price=None,
        job_category=str(org_name)[:80] if org_name else None,
        employment_type=pick_employment_type(str(title)),
        source_url=str(source_url),
        raw_payload={
            "source": workday_site.slug,
            "job_req_id": str(job_req_id),
            "hiring_organization": org_name,
        },
    )


def parse_search_page(
    payload: dict[str, Any],
    settings: Settings,
    workday_site: WorkdaySite,
    error_cls: type[WorkdayFetchError] = WorkdayFetchError,
) -> list[RawListing]:
    postings = payload.get("jobPostings")
    if not isinstance(postings, list):
        msg = "Unexpected Workday search response shape (missing 'jobPostings')"
        raise error_cls(msg)

    parsed: list[RawListing] = []
    for item in postings:
        if not isinstance(item, dict):
            continue
        raw = map_posting(item, settings, workday_site)
        if raw is not None:
            parsed.append(raw)
    return parsed


def post_search(
    settings: Settings,
    workday_site: WorkdaySite,
    applied_facets: dict[str, Any],
    limit: int,
    offset: int,
    error_cls: type[WorkdayFetchError] = WorkdayFetchError,
) -> dict[str, Any]:
    try:
        time.sleep(settings.ingest_rate_limit_seconds)
        response = httpx.post(
            workday_site.search_url,
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
        msg = f"Workday search request failed ({workday_site.slug}): {exc}"
        raise error_cls(msg) from exc

    try:
        return response.json()
    except ValueError as exc:
        msg = f"Workday search response was not valid JSON ({workday_site.slug}): {exc}"
        raise error_cls(msg) from exc


def pick_candidate_location_ids(
    payload: dict[str, Any],
    extra_location_hints: str = "",
    error_cls: type[WorkdayFetchError] = WorkdayFetchError,
) -> list[str]:
    facets = payload.get("facets")
    if not isinstance(facets, list):
        msg = "Unexpected Workday facets response shape (missing 'facets')"
        raise error_cls(msg)

    location_values = _find_location_facet_values(facets)
    extra_hints = {hint.strip().upper() for hint in extra_location_hints.split(",") if hint.strip()}
    hints = LOCATION_HINTS | extra_hints

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


def fetch_workday_listings(
    settings: Settings,
    workday_site: WorkdaySite,
    extra_location_hints: str = "",
    error_cls: type[WorkdayFetchError] = WorkdayFetchError,
) -> list[RawListing]:
    facets_payload = post_search(
        settings,
        workday_site,
        applied_facets={},
        limit=1,
        offset=0,
        error_cls=error_cls,
    )
    location_ids = pick_candidate_location_ids(
        facets_payload,
        extra_location_hints=extra_location_hints,
        error_cls=error_cls,
    )
    if not location_ids:
        return []

    all_items: list[RawListing] = []
    offset = 0
    while True:
        payload = post_search(
            settings,
            workday_site,
            applied_facets={"locations": location_ids},
            limit=PAGE_LIMIT,
            offset=offset,
            error_cls=error_cls,
        )
        all_items.extend(parse_search_page(payload, settings, workday_site, error_cls=error_cls))

        total_found = payload.get("total", 0)
        offset += PAGE_LIMIT
        if offset >= total_found:
            break

    return all_items
