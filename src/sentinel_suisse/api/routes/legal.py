"""Public legal documents (privacy policy + terms of service)."""

from fastapi import APIRouter, Query, Request

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.legal.privacy import POLICY_VERSION, load_privacy_policy
from sentinel_suisse.legal.terms import TERMS_VERSION, load_terms_of_service
from sentinel_suisse.schemas.legal import LegalLanguage, PrivacyPolicyRead, TermsOfServiceRead

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/privacy", response_model=PrivacyPolicyRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_privacy_policy(
    request: Request,
    lang: LegalLanguage = Query(
        default=DEFAULT_LANGUAGE,
        description="Policy language: fr, de, es, pt, or en",
    ),
) -> PrivacyPolicyRead:
    """Return the published privacy policy (nLPD). No authentication required."""
    return PrivacyPolicyRead(
        lang=lang,
        version=POLICY_VERSION,
        content=load_privacy_policy(lang),
    )


@router.get("/terms", response_model=TermsOfServiceRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_terms_of_service(
    request: Request,
    lang: LegalLanguage = Query(
        default=DEFAULT_LANGUAGE,
        description="Terms language: fr, de, es, pt, or en",
    ),
) -> TermsOfServiceRead:
    """Return the published terms of service. No authentication required."""
    return TermsOfServiceRead(
        lang=lang,
        version=TERMS_VERSION,
        content=load_terms_of_service(lang),
    )
