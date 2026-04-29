"""Tag request/response schemas."""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    """Request body for creating a tag."""
    name: str = Field(..., min_length=1, max_length=50)


class TagUpdate(BaseModel):
	"""Request body for updating a tag."""
	name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    """Tag data returned to clients."""

    id: uuid.UUID
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)
