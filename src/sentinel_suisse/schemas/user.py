from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from sentinel_suisse.models.user import User
from sentinel_suisse.security.pii import decrypt_pii


class UserCreate(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime


def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=decrypt_pii(user.email),
        is_active=user.is_active,
        created_at=user.created_at,
    )


class UserCreated(UserRead):
    """Returned once on user creation — api_key is not stored in plaintext."""

    api_key: str = Field(min_length=32)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
