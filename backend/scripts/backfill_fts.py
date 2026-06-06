"""Backfill the FTS search_vector for all existing published posts.

Run from the backend directory:

    uv run python -m scripts.backfill_fts

Uses a direct SQL UPDATE to populate the ``search_vector`` column using
``to_tsvector()``.  The trigger ``trg_posts_search_vector`` handles future
inserts/updates automatically.

Idempotent — running it multiple times is harmless (recomputes the same value).
"""

import asyncio
import logging
import sys

from sqlalchemy import text

sys.path.insert(0, ".")

from app.db.base import async_session_factory  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def backfill() -> None:
    async with async_session_factory() as session:
        # Count posts that need backfilling.
        count_result = await session.execute(text("""
            SELECT COUNT(*) FROM posts
            WHERE status = 'published' AND deleted_at IS NULL
        """))
        total = count_result.scalar()

        if not total:
            logger.info("No published posts found. Nothing to do.")
            return

        logger.info("Backfilling FTS search_vector for %d posts...", total)

        # Direct SQL UPDATE — reliably sets search_vector via to_tsvector().
        result = await session.execute(text("""
            UPDATE posts
            SET search_vector = to_tsvector('english',
                coalesce(title, '') || ' ' || coalesce(content, ''))
            WHERE status = 'published'
              AND deleted_at IS NULL
        """))
        await session.commit()

        logger.info("FTS backfill complete! (%d rows updated)", result.rowcount)


if __name__ == "__main__":
    asyncio.run(backfill())
