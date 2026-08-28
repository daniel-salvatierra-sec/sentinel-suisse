"""France Travail (ex-Pôle Emploi) "Offres d'emploi v2" API — official, OAuth2, no scraping.

Unlike the other connectors, this one talks to a real, documented, sanctioned REST API
(https://francetravail.io) rather than parsing embedded JSON off an HTML search page.
Free registration required to obtain a client_id/client_secret — see
docs/providers/france-travail.md.
"""

import time
from typing import Any

import httpx

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.schemas import RawListing
from sentinel_suisse.models.enums import CountryCode, EmploymentType, ListingType
from sentinel_suisse.services.job_taxonomy import canonical_job_category

_TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"  # noqa: S105
_SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
_SCOPE = "api_offresdemploiv2 o2dsoffre"
_CANDIDATE_DETAIL_URL = "https://candidat.francetravail.fr/offres/recherche/detail/{offer_id}"

_CONTRACT_TYPE_MAP: dict[str, EmploymentType] = {
    "CDI": EmploymentType.PERMANENT,
    "CDD": EmploymentType.TEMPORARY,
    "MIS": EmploymentType.TEMPORARY,
    "SAI": EmploymentType.TEMPORARY,
    "LIB": EmploymentType.FREELANCE,
    "FRA": EmploymentType.FREELANCE,
}


class FranceTravailFetchError(RuntimeError):
    """France Travail API HTTP or parse failure."""


class FranceTravailDisabledError(RuntimeError):
    """Live France Travail ingest is not enabled in settings."""


def _fetch_access_token(settings: Settings) -> str:
    if not settings.france_travail_client_id or not settings.france_travail_client_secret:
        msg = (
            "FRANCE_TRAVAIL_CLIENT_ID / FRANCE_TRAVAIL_CLIENT_SECRET are not set — "
            "register a free app at https://francetravail.io"
        )
        raise FranceTravailFetchError(msg)

    try:
        response = httpx.post(
            _TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.france_travail_client_id,
                "client_secret": settings.france_travail_client_secret,
                "scope": _SCOPE,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        msg = f"France Travail OAuth2 token request failed: {exc}"
        raise FranceTravailFetchError(msg) from exc

    token = response.json().get("access_token")
    if not token:
        msg = "France Travail OAuth2 response did not include an access_token"
        raise FranceTravailFetchError(msg)
    return str(token)


def _pick_employment_type(type_contrat: str | None) -> EmploymentType | None:
    if not type_contrat:
        return None
    return _CONTRACT_TYPE_MAP.get(type_contrat.upper(), EmploymentType.OTHER)


def _pick_source_url(offer: dict[str, Any], offer_id: str) -> str:
    origine = offer.get("origineOffre")
    if isinstance(origine, dict):
        url = origine.get("urlOrigine")
        if url:
            return str(url)
    return _CANDIDATE_DETAIL_URL.format(offer_id=offer_id)


def _map_offer(offer: dict[str, Any]) -> RawListing | None:
    offer_id = offer.get("id")
    title = offer.get("intitule")
    if not offer_id or not title:
        return None

    lieu = offer.get("lieuTravail")
    location = lieu.get("libelle") if isinstance(lieu, dict) else None

    return RawListing(
        external_id=str(offer_id),
        listing_type=ListingType.JOB,
        title=str(title)[:300],
        description=str(offer.get("description"))[:10000] if offer.get("description") else None,
        location=str(location)[:200] if location else None,
        country=CountryCode.FR,
        price=None,
        job_category=canonical_job_category(
            str(offer.get("romeLibelle")) if offer.get("romeLibelle") else None
        ),
        employment_type=_pick_employment_type(offer.get("typeContrat")),
        source_url=_pick_source_url(offer, str(offer_id)),
        raw_payload={"source": "france_travail", "job_id": str(offer_id)},
    )


def parse_search_response(payload: dict[str, Any]) -> list[RawListing]:
    results = payload.get("resultats")
    if not isinstance(results, list):
        msg = "Unexpected France Travail search response shape (missing 'resultats')"
        raise FranceTravailFetchError(msg)

    parsed: list[RawListing] = []
    for offer in results:
        if not isinstance(offer, dict):
            continue
        raw = _map_offer(offer)
        if raw is not None:
            parsed.append(raw)
    return parsed


def fetch_search_listings(settings: Settings, search_url: str | None = None) -> list[RawListing]:
    """Query the official France Travail "Offres d'emploi v2" API. `search_url` is unused —
    kept only to match the other connectors' `fetch_search_listings(settings, search_url)`
    signature used by the ingest CLI."""
    if not settings.ingest_france_travail_live:
        msg = "Live France Travail ingest is disabled (set INGEST_FRANCE_TRAVAIL_LIVE=true)"
        raise FranceTravailDisabledError(msg)

    token = _fetch_access_token(settings)
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": settings.ingest_user_agent,
    }
    parsed: list[RawListing] = []
    seen: set[str] = set()
    page_size = 50
    for page_index in range(settings.france_travail_max_pages):
        start = page_index * page_size
        end = start + page_size - 1
        params: dict[str, str] = {"range": f"{start}-{end}"}
        if settings.france_travail_departement:
            params["departement"] = settings.france_travail_departement
        if settings.france_travail_keywords:
            params["motsCles"] = settings.france_travail_keywords
        try:
            time.sleep(settings.ingest_rate_limit_seconds)
            response = httpx.get(_SEARCH_URL, headers=headers, params=params, timeout=30.0)
            if response.status_code == 204:
                break
            if response.status_code not in (200, 206):
                response.raise_for_status()
        except httpx.HTTPError as exc:
            msg = f"France Travail search request failed: {exc}"
            raise FranceTravailFetchError(msg) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            msg = f"France Travail search response was not valid JSON: {exc}"
            raise FranceTravailFetchError(msg) from exc

        batch = parse_search_response(payload)
        if not batch:
            break
        for item in batch:
            if item.external_id in seen:
                continue
            seen.add(item.external_id)
            parsed.append(item)
        if len(batch) < page_size:
            break
    return parsed
