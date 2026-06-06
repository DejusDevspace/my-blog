"""User Context request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserContextUpdate(BaseModel):
    """Request body for creating or updating user context. All fields optional."""

    bio: str | None = Field(None, max_length=1500)
    interests: list[str] = Field(default_factory=list, max_length=50)
    learning_focus: str | None = Field(None, max_length=1500)
    lifestyle_context: str | None = Field(None, max_length=1500)


class UserContextResponse(BaseModel):
    """User context data returned to clients."""

    id: uuid.UUID
    owner_id: uuid.UUID
    bio: str | None
    interests: list[str]
    learning_focus: str | None
    lifestyle_context: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
