"""Admin comment moderation endpoints — authentication required."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_admin
from app.db.base import get_db
from app.schemas.common import MessageResponse
from app.services import comment_service

router = APIRouter(
    prefix="/admin/comments",
    tags=["Comments (Admin)"],
    dependencies=[Depends(get_current_admin)],
)


@router.delete("/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a comment (hard delete)."""
    deleted = await comment_service.delete_comment(db, comment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )
    return MessageResponse(detail="Comment deleted.")
