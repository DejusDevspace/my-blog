"""Admin tag management endpoints — authentication required."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_admin
from app.db.base import get_db
from app.models.owner import Owner
from app.schemas.common import MessageResponse
from app.schemas.tag import TagCreate, TagResponse, TagUpdate
from app.services import tag_service

router = APIRouter(
    prefix="/admin/tags",
    tags=["Tags (Admin)"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[TagResponse])
async def list_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all tags."""
    return await tag_service.list_tags(db)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[Owner, Depends(get_current_admin)],
):
    """Create a new tag."""
    return await tag_service.create_tag(db, data, admin.id)


@router.patch("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid.UUID,
    data: TagUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an existing tag."""
    tag = await tag_service.update_tag(db, tag_id, data)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found.",
        )
    return tag


@router.delete("/{tag_id}", response_model=MessageResponse)
async def delete_tag(
    tag_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a tag."""
    success = await tag_service.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found.",
        )
    return MessageResponse(detail="Tag deleted.")
