"""Public comment endpoints — no authentication required."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.middleware.rate_limit import comment_rate_limiter
from app.models.owner import Owner
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import comment_service
from sqlalchemy import select

router = APIRouter(tags=["Comments (Public)"])


async def _get_default_owner(db: AsyncSession) -> Owner:
    """Get the single v1 owner for associating comments."""
    result = await db.execute(select(Owner).limit(1))
    owner = result.scalar_one_or_none()
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System not initialised — no owner found.",
        )
    return owner


@router.post("/comments", response_model=CommentResponse, status_code=201)
async def submit_comment(
    data: CommentCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit a comment on a published post.

    Rate limited to 3 per IP per hour. Honeypot field must be empty.
    """
    comment_rate_limiter.check(request)
    owner = await _get_default_owner(db)
    return await comment_service.create_comment(db, data, owner.id)


@router.get(
    "/posts/{slug}/comments",
    response_model=list[CommentResponse],
)
async def get_comments(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all approved comments for a post."""
    from app.services import post_service

    post = await post_service.get_published_post_by_slug(db, slug)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    return await comment_service.list_approved_comments(db, post.id)
