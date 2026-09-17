from pydantic import BaseModel, EmailStr, Field

from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.schemas.user import UserLocale


class MagicLoginRequest(BaseModel):
    email: EmailStr
    locale: UserLocale = DEFAULT_LANGUAGE
    device_token: str | None = Field(default=None, min_length=20, max_length=500)


class MagicLoginRequestResponse(BaseModel):
    sent: bool = True
    api_key: str | None = None
    user_id: int | None = None
    device_token: str | None = None


class MagicLoginConfirm(BaseModel):
    token: str


class MagicLoginConfirmResponse(BaseModel):
    api_key: str
    user_id: int
    device_token: str
