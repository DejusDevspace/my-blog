"""Tag service — business logic for tag management."""

import uuid

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Tag
from app.schemas.tag import TagCreate


async def list_tags(db: AsyncSession, owner_id: uuid.UUID) -> list[Tag]:
    """Return all tags for an owner, ordered by name."""
    result = await db.execute(
        select(Tag).where(Tag.owner_id == owner_id).order_by(Tag.name)
    )
    return list(result.scalars().all())


async def get_or_create_tag(
    db: AsyncSession,
    name: str,
    owner_id: uuid.UUID,
) -> Tag:
    """Return an existing tag by name or create a new one.

    This is used during post creation/update to handle free-form tags.
    """
    slug = slugify(name, max_length=80)

    result = await db.execute(
        select(Tag).where(Tag.owner_id == owner_id, Tag.slug == slug)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    tag = Tag(owner_id=owner_id, name=name, slug=slug)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


async def create_tag(
    db: AsyncSession,
    data: TagCreate,
    owner_id: uuid.UUID,
) -> Tag:
    """Create a new tag (or return existing with same slug)."""
    return await get_or_create_tag(db, data.name, owner_id)


async def delete_tag(
    db: AsyncSession,
    tag_id: uuid.UUID,
) -> bool:
    """Delete a tag by ID. Returns ``False`` if not found."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        return False

    await db.delete(tag)
    await db.flush()
    return True
