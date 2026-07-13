from pydantic import BaseModel, EmailStr, Field, model_validator

from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.schemas.user import UserLocale


class PublicAlertSignup(BaseModel):
    email: EmailStr
    phone: str | None = Field(default=None, min_length=8, max_length=30)
    locale: UserLocale = DEFAULT_LANGUAGE
    query: SearchQuery
    consent: bool = Field(description="User accepted the privacy policy")

    @model_validator(mode="after")
    def validate_signup(self) -> "PublicAlertSignup":
        if not self.consent:
            msg = "Privacy policy consent is required"
            raise ValueError(msg)
        if self.query.listing_type is None:
            msg = "listing_type is required"
            raise ValueError(msg)
        return self


class PublicAlertSignupResponse(BaseModel):
    api_key: str = Field(min_length=32)
    user_id: int
    saved_search_id: int
    email_verified: bool
    whatsapp_verified: bool
    verification_pending: bool
    verification_email_sent: bool = False


class EmailVerificationResponse(BaseModel):
    verified: bool
    channel_type: str = "email"
    message: str
