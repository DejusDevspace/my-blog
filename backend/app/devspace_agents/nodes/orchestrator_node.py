"""Orchestrator node — topic selection and pipeline initialization."""

import json
import logging
from datetime import datetime

from groq import AsyncGroq
from langgraph.types import RunnableConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.devspace_agents.langfuse.client import langfuse
from app.devspace_agents.pipeline.state import AgentState
from app.models.post import Post
from app.services.user_context_service import get_user_context
from app.services.embedding_service import get_embeddings

logger = logging.getLogger(__name__)


async def orchestrator_node(state: AgentState, config: RunnableConfig) -> dict:
    db: AsyncSession = config["configurable"]["db"]
    span = langfuse.start_observation(
        trace_context={"id": state["langfuse_trace_id"]},
        name="orchestrator_node",
        as_type="span",
    )
    try:
        owner_id = state["owner_id"]

        context = await get_user_context(db, owner_id)
        if context is None:
            author_context = {"bio": "", "interests": [], "learning_focus": "", "lifestyle_context": ""}
        else:
            author_context = {
                "bio": context.bio or "",
                "interests": context.interests or [],
                "learning_focus": context.learning_focus or "",
                "lifestyle_context": context.lifestyle_context or "",
            }

        result = await db.execute(
            select(Post)
            .where(
                Post.status == "published",
                Post.deleted_at.is_(None),
                Post.owner_id == owner_id,
            )
            .order_by(Post.published_at.desc())
            .limit(10)
        )
        recent_posts = result.scalars().all()
        recent_post_titles = [p.title for p in recent_posts]

        interests_query = ", ".join(author_context["interests"])
        query_text = interests_query or author_context["learning_focus"] or "technology"
        try:
            vectors = await get_embeddings([query_text])
            if vectors:
                from sqlalchemy import text as sql_text
                from app.models.agent import PostEmbedding

                vec = vectors[0]
                sim_stmt = sql_text("""
                    SELECT DISTINCT ON (pe.post_id)
                        pe.post_id,
                        p.title, p.slug, p.excerpt,
                        1 - (pe.embedding <=> CAST(:vec AS vector)) AS similarity
                    FROM post_embeddings pe
                    JOIN posts p ON pe.post_id = p.id
                    WHERE p.owner_id = :owner_id
                      AND p.status = 'published'
                      AND p.deleted_at IS NULL
                      AND pe.embedding IS NOT NULL
                    ORDER BY pe.post_id, similarity DESC
                    LIMIT 5
                """)
                sim_rows = await db.execute(
                    sim_stmt, {"vec": str(vec), "owner_id": str(owner_id)}
                )
                relevant_past_posts = [
                    {
                        "title": r.title,
                        "slug": r.slug,
                        "excerpt": r.excerpt or "",
                        "similarity": round(float(r.similarity), 4),
                    }
                    for r in sim_rows
                ]
            else:
                relevant_past_posts = []
        except Exception:
            logger.exception("Semantic search failed in orchestrator — continuing without past posts")
            relevant_past_posts = []

        system_prompt = (
            "You are a topic selection assistant for a developer blog. "
            "Return ONLY valid JSON: {\"topic\": \"...\", \"rationale\": \"...\"} "
            "No markdown, no preamble."
        )
        user_prompt = (
            f"Author bio: {author_context['bio']}\n"
            f"Author interests: {author_context['interests']}\n"
            f"Learning focus: {author_context['learning_focus']}\n"
            f"Lifestyle context: {author_context['lifestyle_context']}\n\n"
            f"Recent posts (avoid these topics):\n"
            f"{chr(10).join('- ' + t for t in recent_post_titles)}\n\n"
            "Select a specific, focused blog topic for a developer audience. "
            "Connect to the author's current interests or learning focus. "
            "Be concrete — not 'AI' but 'using embeddings for semantic deduplication in a personal knowledge base.'"
        )

        groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

        generation = span.start_observation(
            name="orchestrator_topic_selection",
            as_type="generation",
            model=settings.GROQ_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        response = await groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content or ""
        generation.update(
            output=response_text,
            usage_details={
                "input": response.usage.prompt_tokens if response.usage else 0,
                "output": response.usage.completion_tokens if response.usage else 0,
            },
        )
        generation.end()

        try:
            parsed = json.loads(response_text)
            topic = parsed["topic"]
            rationale = parsed["rationale"]
        except (json.JSONDecodeError, KeyError):
            retry_generation = span.start_observation(
                name="orchestrator_topic_selection_retry",
                as_type="generation",
                model=settings.GROQ_MODEL,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": response_text},
                    {"role": "user",
                     "content": "Your previous response was not valid JSON. Reply with ONLY: {\"topic\": \"...\", \"rationale\": \"...\"}"},
                ],
            )
            retry_response = await groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": response_text},
                    {"role": "user", "content": "Your previous response was not valid JSON. Reply with ONLY: {\"topic\": \"...\", \"rationale\": \"...\"}"},
                ],
                response_format={"type": "json_object"},
            )
            retry_text = retry_response.choices[0].message.content or ""
            retry_generation.update(
                output=retry_text,
                usage_details={
                    "input": retry_response.usage.prompt_tokens if retry_response.usage else 0,
                    "output": retry_response.usage.completion_tokens if retry_response.usage else 0,
                },
            )
            retry_generation.end()
            parsed = json.loads(retry_text)
            topic = parsed["topic"]
            rationale = parsed["rationale"]

        span.update(status_message="topic_selected")
        span.end()
        return {
            "topic": topic,
            "topic_rationale": rationale,
            "author_context": author_context,
            "relevant_past_posts": relevant_past_posts,
        }

    except Exception as exc:
        span.update(level="ERROR", status_message=str(exc))
        span.end()
        raise RuntimeError(f"orchestrator_node failed: {exc}") from exc
