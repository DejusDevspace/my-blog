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
    """A single search hit, from vector (semantic) and/or full‑text search."""

    post: SearchResultPost
    matched_chunk: str = Field(
        ..., description="The text chunk that best matched the query (vector)."
    )
    similarity: float = Field(
        ..., description="Vector cosine similarity score (0-1, higher is better)."
    )
    aggregated_score: float = Field(
        ...,
        description="Combined relevance score (0-1) taking both vector and FTS into account.",
    )
    match_type: str = Field(
        ...,
        description="How this result matched: 'hybrid', 'semantic', or 'keyword'.",
    )
    highlighted_snippet: str | None = Field(
        None,
        description="Optional FTS-generated excerpt with <mark> tags around matched terms.",
    )


class SemanticSearchResponse(BaseModel):
    """Response wrapper for semantic search."""

    query: str
    results: list[SearchResult]
