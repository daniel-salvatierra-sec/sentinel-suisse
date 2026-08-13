"""Schemas for the optional AI assistant (free-form chat) endpoint."""

from typing import Literal

from pydantic import BaseModel, Field

AssistantLanguage = Literal["fr", "de", "es", "pt", "en"]
AssistantRole = Literal["user", "assistant"]


class AssistantConfig(BaseModel):
    enabled: bool
    max_input_chars: int


class AssistantMessage(BaseModel):
    role: AssistantRole
    content: str = Field(max_length=4000)


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    lang: AssistantLanguage = "fr"
    history: list[AssistantMessage] = Field(default_factory=list)


class AssistantChatResponse(BaseModel):
    reply: str
