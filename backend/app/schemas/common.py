"""Shared schema utilities — pagination, standard responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    limit: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Simple message response for confirmations and errors."""

    detail: str
