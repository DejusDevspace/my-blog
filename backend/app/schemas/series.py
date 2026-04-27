"""Series request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class SeriesCreate(BaseModel):
    """Request body for creating a series."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    status: str = Field(default="draft", pattern=r"^(draft|published)$")


class SeriesUpdate(BaseModel):
    """Request body for updating a series. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=250)
    description: str | None = Field(None, max_length=1000)
    status: str | None = Field(None, pattern=r"^(draft|published)$")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class SeriesListItem(BaseModel):
    """Series data for list views — includes post count."""

    id: uuid.UUID
    title: str
    slug: str
    description: str | None
    status: str
    post_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeriesPostItem(BaseModel):
    """Minimal post data when shown inside a series response."""

    id: uuid.UUID
    title: str
    slug: str
    series_order: int | None
    status: str
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class SeriesResponse(BaseModel):
    """Full series data with its ordered posts."""

    id: uuid.UUID
    title: str
    slug: str
    description: str | None
    status: str
    posts: list[SeriesPostItem]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
