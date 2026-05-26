"""Backfill embeddings for all published posts.

Run from the backend directory:

    uv run python -m scripts.backfill_embeddings

This is a one-off script to generate embeddings for posts that existed
before the embedding pipeline was deployed.
"""

import asyncio
import logging
import sys

from sqlalchemy import func, select

# Ensure the app package is importable.
sys.path.insert(0, ".")

from app.db.base import async_session_factory  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.agent import PostEmbedding  # noqa: E402
from app.services.embedding_service import generate_post_embeddings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def backfill() -> None:
    """Generate embeddings for all published posts that don't have them yet."""
    async with async_session_factory() as session:
        # Find published posts without embeddings.
        subq = (
            select(PostEmbedding.post_id)
            .group_by(PostEmbedding.post_id)
            .having(func.count() > 0)
        )
        stmt = (
            select(Post)
            .where(
                Post.status == "published",
                Post.deleted_at.is_(None),
                Post.id.not_in(subq),
            )
            .order_by(Post.published_at.desc())
        )
        result = await session.execute(stmt)
        posts = list(result.scalars().all())

        if not posts:
            logger.info("All published posts already have embeddings. Nothing to do.")
            return

        logger.info("Found %d posts without embeddings. Starting backfill...", len(posts))

        for i, post in enumerate(posts, 1):
            logger.info(
                "[%d/%d] Embedding: %s", i, len(posts), post.title
            )
            try:
                await generate_post_embeddings(session, post.id)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to embed post: %s", post.title)

        logger.info("Backfill complete!")


if __name__ == "__main__":
    asyncio.run(backfill())
