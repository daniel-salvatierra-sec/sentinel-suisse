from pydantic import BaseModel, EmailStr

from sentinel_suisse.i18n import DEFAULT_LANGUAGE
from sentinel_suisse.schemas.user import UserLocale


class MagicLoginRequest(BaseModel):
    email: EmailStr
    locale: UserLocale = DEFAULT_LANGUAGE


class MagicLoginRequestResponse(BaseModel):
    sent: bool = True


class MagicLoginConfirm(BaseModel):
    token: str


class MagicLoginConfirmResponse(BaseModel):
    api_key: str
    user_id: int
