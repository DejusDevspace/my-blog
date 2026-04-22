"""Public post endpoints — no authentication required."""

import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.post import PostListItem, PostResponse
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["Posts (Public)"])


@router.get("", response_model=PaginatedResponse[PostListItem])
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


@router.get("/{slug}", response_model=PostResponse)
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
