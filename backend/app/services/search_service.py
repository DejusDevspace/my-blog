"""Search service — vector similarity queries against post embeddings."""

import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import PostEmbedding
from app.models.post import Post
from app.schemas.search import SearchResult, SearchResultPost
from app.services.embedding_service import get_embeddings

logger = logging.getLogger(__name__)


async def semantic_search(
    db: AsyncSession,
    query: str,
    *,
    limit: int = 10,
) -> list[SearchResult]:
    """Embed the query and find the closest post chunks via cosine similarity.

    Results are deduplicated by post — only the best-matching chunk per post
    is returned, ordered by similarity (highest first).
    """
    # Generate the query embedding.
    vectors = await get_embeddings([query])
    if not vectors:
        return []

    query_vector = vectors[0]

    # Build the similarity query.
    # We use (1 - cosine_distance) to get a similarity score in [0, 1].
    stmt = (
        select(
            PostEmbedding.post_id,
            PostEmbedding.chunk_text,
            (1 - PostEmbedding.embedding.cosine_distance(query_vector)).label(
                "similarity"
            ),
            Post.title,
            Post.slug,
            Post.excerpt,
            Post.id.label("pid"),
        )
        .join(Post, PostEmbedding.post_id == Post.id)
        .where(
            Post.status == "published",
            Post.deleted_at.is_(None),
            PostEmbedding.embedding.is_not(None),
            # (1 - PostEmbedding.embedding.cosine_distance(query_vector)),
        )
        .order_by(text("similarity DESC"))
        .limit(limit * 3)  # Over-fetch to allow deduplication.
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Deduplicate by post — keep the chunk with highest similarity.
    seen_posts: set = set()
    results: list[SearchResult] = []

    for row in rows:
        # if float(row.similarity) < 0.20:
        #     break

        if row.post_id in seen_posts:
            continue
        seen_posts.add(row.post_id)

        results.append(
            SearchResult(
                post=SearchResultPost(
                    id=row.pid,
                    title=row.title,
                    slug=row.slug,
                    excerpt=row.excerpt,
                ),
                matched_chunk=row.chunk_text,
                similarity=round(float(row.similarity), 4),
            )
        )

        if len(results) >= limit:
            break

    print("SEARCH RESULTS:", results)

    return results
