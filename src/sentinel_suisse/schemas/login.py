from pydantic import BaseModel, EmailStr, Field

from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.schemas.user import UserLocale
from sentinel_suisse.security.passwords import MAX_PASSWORD_LEN, MIN_PASSWORD_LEN


class MagicLoginRequest(BaseModel):
    email: EmailStr
    # No min_length here: short wrong passwords must return invalid_credentials, not 422.
    password: str | None = Field(default=None, max_length=MAX_PASSWORD_LEN)
    locale: UserLocale = DEFAULT_LANGUAGE
    device_token: str | None = Field(default=None, min_length=20, max_length=500)


class MagicLoginRequestResponse(BaseModel):
    sent: bool = False
    api_key: str | None = None
    user_id: int | None = None
    device_token: str | None = None
    needs_password: bool = False
    invalid_credentials: bool = False


class MagicLoginConfirm(BaseModel):
    token: str


class MagicLoginConfirmResponse(BaseModel):
    api_key: str
    user_id: int
    device_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    locale: UserLocale = DEFAULT_LANGUAGE


class ForgotPasswordResponse(BaseModel):
    sent: bool = True


class SetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    password: str = Field(min_length=MIN_PASSWORD_LEN, max_length=MAX_PASSWORD_LEN)


class SetPasswordResponse(BaseModel):
    api_key: str
    user_id: int
    device_token: str
