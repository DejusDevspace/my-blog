"""Debug / diagnostic endpoints — read-only, no auth."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.base import get_db

router = APIRouter(tags=["Debug"])


@router.get("/debug")
async def debug_info(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return diagnostic information about the application and database."""
    rows = await db.execute(text("SELECT COUNT(*) FROM posts"))
    total_posts = rows.scalar()

    rows = await db.execute(text(
        "SELECT COUNT(*) FROM posts WHERE status = 'published' AND deleted_at IS NULL"
    ))
    published_posts = rows.scalar()

    rows = await db.execute(text(
        "SELECT COUNT(*) FROM posts WHERE status = 'draft' AND deleted_at IS NULL"
    ))
    draft_posts = rows.scalar()

    rows = await db.execute(text(
        "SELECT COUNT(*) FROM posts WHERE search_vector IS NOT NULL"
    ))
    posts_with_fts = rows.scalar()

    rows = await db.execute(text(
        "SELECT COUNT(*) FROM post_embeddings GROUP BY post_id"
    ))
    posts_with_embeddings = len(rows.all())

    rows = await db.execute(text("SELECT COUNT(*) FROM owners"))
    owners = rows.scalar()

    rows = await db.execute(text("SELECT COUNT(*) FROM categories"))
    categories = rows.scalar()

    rows = await db.execute(text("SELECT COUNT(*) FROM tags"))
    tags = rows.scalar()

    rows = await db.execute(text("SELECT COUNT(*) FROM series"))
    series_count = rows.scalar()

    rows = await db.execute(text("SELECT COUNT(*) FROM comments"))
    comments = rows.scalar()

    rows = await db.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'posts' AND indexname = 'ix_posts_search_vector_gin'
    """))
    fts_index = rows.fetchone() is not None

    return {
        "app": {
            "name": "d3jusdevspace API",
            "version": "0.1.0",
        },
        "database": {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": draft_posts,
            "posts_with_fts_vector": posts_with_fts,
            "posts_with_embeddings": posts_with_embeddings,
            "owners": owners,
            "categories": categories,
            "tags": tags,
            "series": series_count,
            "comments": comments,
        },
        "fts_infrastructure": {
            "search_vector_column": True,
            "gin_index_exists": fts_index,
        },
    }
