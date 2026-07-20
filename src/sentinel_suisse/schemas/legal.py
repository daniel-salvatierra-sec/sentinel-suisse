from typing import Literal

from pydantic import BaseModel, Field

from sentinel_suisse.i18n import SUPPORTED_LANGUAGES

PrivacyLanguage = Literal["fr", "de", "es", "pt", "en"]
LegalLanguage = PrivacyLanguage


class PrivacyPolicyRead(BaseModel):
    lang: PrivacyLanguage
    version: str
    content: str
    erasure_endpoint: str = Field(default="/api/v1/users/me")
    supported_languages: list[str] = Field(default_factory=lambda: sorted(SUPPORTED_LANGUAGES))


class TermsOfServiceRead(BaseModel):
    lang: LegalLanguage
    version: str
    content: str
    privacy_endpoint: str = Field(default="/api/v1/legal/privacy")
    supported_languages: list[str] = Field(default_factory=lambda: sorted(SUPPORTED_LANGUAGES))


class RefundPolicyRead(BaseModel):
    version: str
    content: str
    endpoint: str = Field(default="/api/v1/legal/refunds")
