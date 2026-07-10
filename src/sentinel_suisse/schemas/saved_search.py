from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from sentinel_suisse.schemas.search import SearchQuery


class SavedSearchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    query: SearchQuery
    is_active: bool = True


class SavedSearchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    query: SearchQuery | None = None
    is_active: bool | None = None


class SavedSearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    query: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
