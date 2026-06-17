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


class AdminStatsResponse(BaseModel):
    """Aggregated dashboard statistics, owner-scoped."""

    total_posts: int
    published_posts: int
    draft_posts: int
    agent_pending_posts: int
    total_comments: int
    pending_comments: int
    total_categories: int
    total_tags: int
    agent_runs_total: int
    agent_runs_failed: int
    agent_runs_today: int
