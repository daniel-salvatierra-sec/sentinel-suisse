"""Public listing-text translation (in-app reading language)."""

from typing import Literal

from pydantic import BaseModel, Field

TranslateLanguage = Literal["fr", "de", "es", "pt", "en"]


class PublicTranslateIn(BaseModel):
    lang: TranslateLanguage
    title: str = Field(default="", max_length=500)
    body: str = Field(default="", max_length=7500)


class PublicTranslateOut(BaseModel):
    title: str
    body: str
