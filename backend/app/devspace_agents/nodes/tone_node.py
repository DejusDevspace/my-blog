"""Tone node — writing style analysis from the published post corpus."""

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

logger = logging.getLogger(__name__)

_TONE_SAMPLE_SIZE = 10
_TONE_FALLBACK = (
    "Write in a clear, practical, developer-focused style. "
    "Use short paragraphs and concrete examples over abstract theory. "
    "Keep a direct, confident tone."
)


async def tone_node(state: AgentState, config: RunnableConfig) -> dict:
    db: AsyncSession = config["configurable"]["db"]
    span = langfuse.span(
        trace_id=state["langfuse_trace_id"],
        name="tone_node",
    )
    try:
        owner_id = state["owner_id"]

        result = await db.execute(
            select(Post)
            .where(
                Post.status == "published",
                Post.deleted_at.is_(None),
                Post.owner_id == owner_id,
            )
            .order_by(Post.published_at.desc())
            .limit(_TONE_SAMPLE_SIZE)
        )
        posts = result.scalars().all()

        if len(posts) < 3:
            logger.warning("Fewer than 3 published posts — using fallback tone profile.")
            span.update(status_message="fallback_used_corpus_too_small")
            span.end()
            return {"tone_profile": _TONE_FALLBACK}

        corpus_text = "\n---\n".join(
            f"Title: {p.title}\nExcerpt: {p.excerpt or ''}\nContent start: {p.content[:500]}"
            for p in posts
        )

        system_prompt = (
            "You are a writing style analyst. Given a sample of an author's published blog posts, "
            "describe their writing style in 2-3 sentences. Focus on: sentence structure, vocabulary "
            "level, use of examples vs theory, humour or formality, and paragraph length. "
            "Return ONLY valid JSON: {\"tone_profile\": \"...\"} No markdown, no preamble."
        )
        user_prompt = f"Here are the author's recent posts:\n\n{corpus_text}"

        groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

        generation = langfuse.generation(
            trace_id=state["langfuse_trace_id"],
            parent_observation_id=span.id,
            name="tone_style_analysis",
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
            usage={
                "input": response.usage.prompt_tokens if response.usage else 0,
                "output": response.usage.completion_tokens if response.usage else 0,
            },
        )

        try:
            parsed = json.loads(response_text)
            tone_profile = parsed["tone_profile"]
        except (json.JSONDecodeError, KeyError):
            tone_profile = response_text

        span.update(status_message=f"analysed_{len(posts)}_posts")
        span.end()
        return {"tone_profile": tone_profile}

    except Exception as exc:
        span.update(level="ERROR", status_message=str(exc))
        span.end()
        raise RuntimeError(f"tone_node failed: {exc}") from exc
