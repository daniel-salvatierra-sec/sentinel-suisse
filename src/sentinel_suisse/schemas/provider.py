from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")
    base_url: HttpUrl
    is_active: bool = True


class ProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")
    base_url: HttpUrl | None = None
    is_active: bool | None = None


class ProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    base_url: str
    is_active: bool
