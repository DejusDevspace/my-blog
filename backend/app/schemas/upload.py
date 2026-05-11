"""Upload response schemas."""

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """Response returned after a successful image upload."""

    url: str


class ImageDeleteRequest(BaseModel):
    """Request body for deleting a previously uploaded image."""

    url: str
