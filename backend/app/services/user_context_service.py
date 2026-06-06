"""User Context service — logic for managing owner context profiles."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_context import UserContext
from app.schemas.user_context import UserContextUpdate


async def get_user_context(db: AsyncSession, owner_id: uuid.UUID) -> UserContext | None:
    """Fetch the context for a specific owner."""
    result = await db.execute(select(UserContext).where(UserContext.owner_id == owner_id))
    return result.scalar_one_or_none()


async def upsert_user_context(
    db: AsyncSession,
    owner_id: uuid.UUID,
    data: UserContextUpdate,
) -> UserContext:
    """Create or update the context for an owner."""
    result = await db.execute(select(UserContext).where(UserContext.owner_id == owner_id))
    context = result.scalar_one_or_none()

    if context is None:
        # Create new context
        context = UserContext(
            owner_id=owner_id,
            bio=data.bio,
            interests=data.interests,
            learning_focus=data.learning_focus,
            lifestyle_context=data.lifestyle_context,
        )
        db.add(context)
    else:
        # Update existing context
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(context, field, value)

    await db.flush()
    await db.refresh(context)
    return context
