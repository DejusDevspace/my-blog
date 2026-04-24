"""Category service — business logic for category CRUD."""

import uuid

from slugify import slugify
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.post import Post
from app.schemas.category import CategoryCreate, CategoryUpdate


async def list_categories(db: AsyncSession) -> list[Category]:
    """Return all categories ordered by name."""
    result = await db.execute(select(Category).order_by(Category.name))
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
    """Fetch a single category by ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def create_category(
    db: AsyncSession,
    data: CategoryCreate,
    owner_id: uuid.UUID,
) -> Category:
    """Create a new category with an auto-generated slug."""
    slug = slugify(data.name, max_length=120)

    # Check for duplicate slug under this owner.
    existing = await db.execute(
        select(Category.id).where(
            Category.owner_id == owner_id,
            Category.slug == slug,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with slug '{slug}' already exists.",
        )

    category = Category(
        owner_id=owner_id,
        name=data.name,
        slug=slug,
        description=data.description,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    category_id: uuid.UUID,
    data: CategoryUpdate,
    owner_id: uuid.UUID,
) -> Category | None:
    """Update an existing category. Returns ``None`` if not found."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    if category is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # If name changed but slug not explicitly set, regenerate slug.
    if "name" in update_data and "slug" not in update_data:
        update_data["slug"] = slugify(update_data["name"], max_length=120)

    # If slug explicitly provided, normalise it.
    if "slug" in update_data:
        update_data["slug"] = slugify(update_data["slug"], max_length=120)

    # Validate slug uniqueness.
    if "slug" in update_data:
        existing = await db.execute(
            select(Category.id).where(
                Category.owner_id == owner_id,
                Category.slug == update_data["slug"],
                Category.id != category_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category slug '{update_data['slug']}' is already in use.",
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    await db.flush()
    await db.refresh(category)
    return category


async def delete_category(
    db: AsyncSession,
    category_id: uuid.UUID,
) -> None:
    """Delete a category. Raises if posts are still assigned to it."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    # Block deletion if posts reference this category.
    post_count_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.category_id == category_id,
            Post.deleted_at.is_(None),
        )
    )
    post_count = post_count_result.scalar() or 0

    if post_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot delete category: {post_count} post(s) are still assigned to it. "
                "Please reassign them to another category first."
            ),
        )

    await db.delete(category)
    await db.flush()
