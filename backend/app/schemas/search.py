"""Semantic search request/response schemas."""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class SearchResultPost(BaseModel):
    """Lightweight post data embedded in search results."""

    id: uuid.UUID
    title: str
    slug: str
    excerpt: str | None

    model_config = ConfigDict(from_attributes=True)


class SearchResult(BaseModel):
    """A single semantic search hit."""

    post: SearchResultPost
    matched_chunk: str = Field(
        ..., description="The text chunk that best matched the query."
    )
    similarity: float = Field(
        ..., description="Cosine similarity score (0-1, higher is better)."
    )


class SemanticSearchResponse(BaseModel):
    """Response wrapper for semantic search."""

    query: str
    results: list[SearchResult]
