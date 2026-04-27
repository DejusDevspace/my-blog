"""Admin series management endpoints — authentication required."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_admin
from app.db.base import get_db
from app.models.owner import Owner
from app.schemas.common import MessageResponse
from app.schemas.series import (
    SeriesCreate,
    SeriesListItem,
    SeriesResponse,
    SeriesUpdate,
)
from app.services import series_service

router = APIRouter(
    prefix="/admin/series",
    tags=["Series (Admin)"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[SeriesListItem])
async def list_all_series(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status: draft, published",
    ),
):
    """List all series with post counts."""
    return await series_service.list_series(db, status_filter=status_filter)


@router.get("/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single series with its ordered posts."""
    series = await series_service.get_series_by_id(db, series_id)
    if series is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found.",
        )
    return series


@router.post("", response_model=SeriesResponse, status_code=201)
async def create_series(
    data: SeriesCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[Owner, Depends(get_current_admin)],
):
    """Create a new series."""
    return await series_service.create_series(db, data, admin.id)


@router.patch("/{series_id}", response_model=SeriesResponse)
async def update_series(
    series_id: uuid.UUID,
    data: SeriesUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an existing series."""
    series = await series_service.update_series(db, series_id, data)
    if series is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found.",
        )
    return series


@router.delete("/{series_id}", response_model=MessageResponse)
async def delete_series(
    series_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a series. Posts are detached, not deleted."""
    await series_service.delete_series(db, series_id)
    return MessageResponse(detail="Series deleted. Posts have been detached.")
