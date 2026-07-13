"""Public legal documents (privacy policy)."""

from typing import Literal

from fastapi import APIRouter, Query, Request

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.legal.privacy import POLICY_VERSION, load_privacy_policy
from sentinel_suisse.schemas.legal import PrivacyPolicyRead

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/privacy", response_model=PrivacyPolicyRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_privacy_policy(
    request: Request,
    lang: Literal["fr", "de"] = Query(default="fr", description="Policy language (fr or de)"),
) -> PrivacyPolicyRead:
    """Return the published privacy policy (nLPD / nDSG). No authentication required."""
    return PrivacyPolicyRead(
        lang=lang,
        version=POLICY_VERSION,
        content=load_privacy_policy(lang),
    )
