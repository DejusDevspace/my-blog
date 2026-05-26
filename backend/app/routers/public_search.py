"""Public semantic search endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.base import get_db
from app.schemas.search import SemanticSearchResponse
from app.services import search_service

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(
        ...,
        min_length=2,
        max_length=500,
        description="Natural-language search query.",
    ),
    limit: int = Query(10, ge=1, le=50),
):
    """Search posts by semantic meaning.

    Embeds the query and finds the most similar post chunks using
    cosine similarity over pgvector embeddings.
    """
    try:
        results = await search_service.semantic_search(db, q, limit=limit)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return SemanticSearchResponse(query=q, results=results)
