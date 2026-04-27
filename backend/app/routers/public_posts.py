"""Public post and series endpoints — no authentication required."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.post import PostListItem, PostResponse
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse
from app.schemas.series import SeriesListItem, SeriesResponse
from app.services import post_service, category_service, tag_service, series_service

router = APIRouter(prefix="", tags=["Public API"])

@router.get("/categories", response_model=list[CategoryResponse])
async def get_public_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    """List all categories for the public feed."""
    return await category_service.list_categories(db)

@router.get("/tags", response_model=list[TagResponse])
async def get_public_tags(db: Annotated[AsyncSession, Depends(get_db)]):
    """List all tags for the public feed."""
    return await tag_service.list_tags(db)

@router.get("/series", response_model=list[SeriesListItem])
async def list_public_series(db: Annotated[AsyncSession, Depends(get_db)]):
    """List all published series with post counts."""
    return await series_service.list_published_series(db)


@router.get("/series/{slug}", response_model=SeriesResponse)
async def get_series(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single published series with its ordered posts."""
    series = await series_service.get_series_by_slug(db, slug)
    if series is None or series.status != "published":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found.",
        )
    return series

@router.get("/posts", response_model=PaginatedResponse[PostListItem])
async def list_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(None, description="Filter by category slug"),
    tag: str | None = Query(None, description="Filter by tag slug"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
):
    """List published posts with optional category/tag filters."""
    posts, total = await post_service.list_published_posts(
        db, category_slug=category, tag_slug=tag, page=page, limit=limit
    )
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )


@router.get("/posts/{slug}", response_model=PostResponse)
async def get_post(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single published post by slug."""
    post = await post_service.get_published_post_by_slug(db, slug)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    return post
