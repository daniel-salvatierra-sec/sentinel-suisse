"""Public legal documents (privacy policy + terms of service)."""

from pathlib import Path

from fastapi import APIRouter, Query, Request

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.legal.privacy import POLICY_VERSION, load_privacy_policy
from sentinel_suisse.legal.terms import TERMS_VERSION, load_terms_of_service
from sentinel_suisse.schemas.legal import (
    LegalLanguage,
    PrivacyPolicyRead,
    RefundPolicyRead,
    TermsOfServiceRead,
)

router = APIRouter(prefix="/legal", tags=["legal"])

_REFUNDS_VERSION = "2026-07-20"
_REFUNDS_PATH = Path(__file__).resolve().parents[4] / "docs" / "legal" / "refunds.md"


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


@router.get("/refunds", response_model=RefundPolicyRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_refund_policy(request: Request) -> RefundPolicyRead:
    """Return the draft Premium refund policy (Markdown). No authentication required."""
    content = (
        _REFUNDS_PATH.read_text(encoding="utf-8")
        if _REFUNDS_PATH.is_file()
        else "# Refund policy\n\nDocument pending.\n"
    )
    return RefundPolicyRead(version=_REFUNDS_VERSION, content=content)
