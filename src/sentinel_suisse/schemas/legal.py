from typing import Literal

from pydantic import BaseModel, Field


class PrivacyPolicyRead(BaseModel):
    lang: Literal["fr", "de"]
    version: str
    content: str
    erasure_endpoint: str = Field(default="/api/v1/users/me")
