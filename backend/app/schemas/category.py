"""Category request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Request body for creating a category."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class CategoryUpdate(BaseModel):
    """Request body for updating a category. All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)


class CategoryResponse(BaseModel):
    """Category data returned to clients."""

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
