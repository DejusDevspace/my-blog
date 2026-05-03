"""Series service — business logic for series CRUD."""

import uuid
from datetime import datetime

from slugify import slugify
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.series import Series
from app.schemas.series import SeriesCreate, SeriesUpdate


async def _generate_unique_slug(
    db: AsyncSession,
    title: str,
    *,
    exclude_series_id: uuid.UUID | None = None,
) -> str:
    """Generate a URL-safe slug, appending a suffix on collision."""
    base_slug = slugify(title, max_length=200)
    slug = base_slug
    counter = 1

    while True:
        query = select(Series.id).where(Series.slug == slug)
        if exclude_series_id is not None:
            query = query.where(Series.id != exclude_series_id)
        result = await db.execute(query)
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


async def list_series(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
) -> list[dict]:
    """Return all series with post counts.

    Returns dicts so we can attach the computed ``post_count`` field.
    """
    query = select(Series).order_by(Series.created_at.desc())
    if status_filter:
        query = query.where(Series.status == status_filter)

    result = await db.execute(query)
    series_list = list(result.scalars().unique().all())

    items = []
    for s in series_list:
        # Count non-deleted posts in this series.
        count_result = await db.execute(
            select(func.count(Post.id)).where(
                Post.series_id == s.id,
                Post.deleted_at.is_(None),
            )
        )
        post_count = count_result.scalar() or 0
        items.append({
            "id": s.id,
            "title": s.title,
            "slug": s.slug,
            "description": s.description,
            "status": s.status,
            "post_count": post_count,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        })
    return items


async def list_published_series(db: AsyncSession) -> list[dict]:
    """Public endpoint — only published series."""
    return await list_series(db, status_filter="published")


async def get_series_by_slug(
    db: AsyncSession,
    slug: str,
) -> Series | None:
    """Fetch a single series by slug with its ordered posts."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Series)
        .where(Series.slug == slug)
        .options(selectinload(Series.posts))
    )
    return result.scalar_one_or_none()


async def get_series_by_id(
    db: AsyncSession,
    series_id: uuid.UUID,
) -> Series | None:
    """Fetch a single series by ID."""
    result = await db.execute(select(Series).where(Series.id == series_id))
    return result.scalar_one_or_none()


async def create_series(
    db: AsyncSession,
    data: SeriesCreate,
    owner_id: uuid.UUID,
) -> Series:
    """Create a new series with an auto-generated slug."""
    slug = await _generate_unique_slug(db, data.title)

    series = Series(
        owner_id=owner_id,
        title=data.title,
        slug=slug,
        description=data.description,
        status=data.status,
    )
    db.add(series)
    await db.flush()
    await db.refresh(series, attribute_names=["posts"])
    return series


async def update_series(
    db: AsyncSession,
    series_id: uuid.UUID,
    data: SeriesUpdate,
) -> Series | None:
    """Update an existing series. Returns ``None`` if not found."""
    result = await db.execute(select(Series).where(Series.id == series_id))
    series = result.scalar_one_or_none()
    if series is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Regenerate slug if title changed but slug not explicitly set.
    if "title" in update_data and "slug" not in update_data:
        update_data["slug"] = await _generate_unique_slug(
            db, update_data["title"], exclude_series_id=series_id
        )

    # Validate slug uniqueness if explicitly provided.
    if "slug" in update_data:
        slug_val = slugify(update_data["slug"], max_length=200)
        existing = await db.execute(
            select(Series.id).where(Series.slug == slug_val, Series.id != series_id)
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Series slug '{slug_val}' is already in use.",
            )
        update_data["slug"] = slug_val

    for field, value in update_data.items():
        setattr(series, field, value)

    await db.flush()
    await db.refresh(series, attribute_names=["posts"])
    return series


async def delete_series(
    db: AsyncSession,
    series_id: uuid.UUID,
) -> None:
    """Delete a series. Posts are detached (series_id set to NULL via ON DELETE SET NULL)."""
    result = await db.execute(select(Series).where(Series.id == series_id))
    series = result.scalar_one_or_none()
    if series is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found.",
        )

    await db.delete(series)
    await db.flush()
