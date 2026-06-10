"""Context embedding service — vector generation for UserContext fields.

This service handles UserContext field embeddings stored in the
context_embeddings table. These embeddings are used by context_node
to find which author context fields are most relevant to a given topic.
"""

import logging
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session_factory
from app.models.agent import ContextEmbedding
from app.models.user_context import UserContext
from app.services.embedding_service import get_embeddings

logger = logging.getLogger(__name__)

_EMBEDDABLE_FIELDS = ["bio", "learning_focus", "lifestyle_context"]


async def generate_context_embeddings(
    db: AsyncSession,
    owner_id: uuid.UUID,
) -> None:
    """Generate and store embeddings for all embeddable UserContext fields.

    Replaces any existing ContextEmbedding rows for the owner (idempotent).
    """
    result = await db.execute(
        select(UserContext).where(UserContext.owner_id == owner_id)
    )
    context = result.scalar_one_or_none()
    if context is None:
        logger.warning("No UserContext found for owner %s — nothing to embed.", owner_id)
        return

    pairs: list[tuple[str, str]] = []
    for field in _EMBEDDABLE_FIELDS:
        value = getattr(context, field, None)
        if value and str(value).strip():
            pairs.append((field, str(value)))

    if context.interests:
        interests_text = ", ".join(context.interests)
        pairs.append(("interests", interests_text))

    if not pairs:
        logger.info("No non-empty context fields for owner %s.", owner_id)
        return

    texts = [text for _, text in pairs]

    try:
        vectors = await get_embeddings(texts)
    except Exception:
        logger.exception("Failed to generate context embeddings for owner %s", owner_id)
        return

    if len(vectors) != len(pairs):
        logger.error(
            "Embedding count mismatch for owner %s: %d pairs, %d vectors",
            owner_id, len(pairs), len(vectors),
        )
        return

    await db.execute(
        delete(ContextEmbedding).where(ContextEmbedding.owner_id == owner_id)
    )

    for (field_key, _), vector in zip(pairs, vectors):
        db.add(
            ContextEmbedding(
                owner_id=owner_id,
                field_key=field_key,
                embedding=vector,
            )
        )

    await db.flush()
    logger.info(
        "Generated %d context embeddings for owner %s", len(pairs), owner_id
    )


async def generate_context_embeddings_background(owner_id: uuid.UUID) -> None:
    """Background-task wrapper — opens its own DB session."""
    async with async_session_factory() as session:
        try:
            await generate_context_embeddings(session, owner_id)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception(
                "Background context embedding generation failed for owner %s", owner_id
            )
