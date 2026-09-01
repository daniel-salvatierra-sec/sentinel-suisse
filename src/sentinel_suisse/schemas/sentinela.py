"""Sentinela turn: UI actions instead of chat-only replies."""

from typing import Any, Literal

from pydantic import BaseModel, Field

SentinelaLocale = Literal["fr", "de", "es", "pt", "en"]
SentinelaMode = Literal["housing", "job"]
SentinelaTab = Literal["list", "map", "alerts", "account", "overview", "publish"]
SentinelaZone = Literal["CH", "FR", "DE", "IT"]
SentinelaActionType = Literal[
    "set_mode",
    "apply_filters",
    "run_search",
    "switch_tab",
    "open_listing",
    "highlight_listings",
    "focus_map",
    "compose_alert",
    "point_to",
    "suggest_chips",
    "open_guide",
]
SentinelaSayId = Literal[
    "filtered",
    "empty",
    "need_city",
    "unknown_city",
    "alert",
    "open_first",
    "open_listing",
    "map",
    "out_of_scope",
    "guide",
]


class SentinelaOpenListing(BaseModel):
    id: int | None = None
    location: str | None = None
    price: int | float | None = None


class SentinelaUiContext(BaseModel):
    tab: SentinelaTab = "list"
    mode: SentinelaMode = "housing"
    zone: SentinelaZone = "CH"
    query: str = ""
    rooms: str = ""
    price_max: str = ""
    has_session: bool = False
    result_count: int = 0
    open_listing: SentinelaOpenListing | None = None


class SentinelaTurnRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    locale: SentinelaLocale = "fr"
    ui_context: SentinelaUiContext = Field(default_factory=SentinelaUiContext)


class SentinelaAction(BaseModel):
    type: SentinelaActionType
    payload: dict[str, Any] = Field(default_factory=dict)


class SentinelaTurnResponse(BaseModel):
    actions: list[SentinelaAction]
    say_id: SentinelaSayId
    slots: dict[str, str] = Field(default_factory=dict)
    chips: list[str] = Field(default_factory=list)
