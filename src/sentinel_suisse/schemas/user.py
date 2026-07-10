from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_active: bool
    created_at: datetime


class UserCreated(UserRead):
    """Returned once on user creation — api_key is not stored in plaintext."""

    api_key: str = Field(min_length=32)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
