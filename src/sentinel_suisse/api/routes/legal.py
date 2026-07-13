"""Public legal documents (privacy policy)."""

from fastapi import APIRouter, Query, Request

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.legal.privacy import POLICY_VERSION, load_privacy_policy
from sentinel_suisse.schemas.legal import PrivacyLanguage, PrivacyPolicyRead

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/privacy", response_model=PrivacyPolicyRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_privacy_policy(
    request: Request,
    lang: PrivacyLanguage = Query(
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
