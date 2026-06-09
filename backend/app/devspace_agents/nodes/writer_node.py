"""Writer node — draft post generation."""

import json
import logging
import uuid

from groq import AsyncGroq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.devspace_agents.langfuse.client import langfuse
from app.devspace_agents.pipeline.state import AgentState
from app.models.category import Category

logger = logging.getLogger(__name__)


async def writer_node(state: AgentState, db: AsyncSession) -> dict:
    span = langfuse.span(
        trace_id=state["langfuse_trace_id"],
        name="writer_node",
    )
    try:
        owner_id = state["owner_id"]

        result = await db.execute(
            select(Category).where(Category.owner_id == owner_id)
        )
        categories = result.scalars().all()
        category_list = [{"id": str(c.id), "name": c.name} for c in categories]

        langfuse.event(
            trace_id=state["langfuse_trace_id"],
            parent_observation_id=span.id,
            name="writer_category_fetch",
            output={"categories": [c.name for c in categories]},
        )

        tone = state.get("tone_profile", _TONE_FALLBACK)
        author = state.get("author_context", {})
        research = state.get("research_summary", "")
        past_posts = state.get("relevant_past_posts", [])

        category_hint = ""
        if category_list:
            category_hint = "\n".join(
                f'  - {c["name"]} (id: {c["id"]})' for c in category_list
            )

        past_titles = "\n".join(
            f'  - {p.get("title", "")}' for p in past_posts
        )

        system_prompt = (
            "You are a technical blog post writer. Write a complete markdown blog post "
            f"in the following style:\n\n{tone}\n\n"
            f"Author context — bio: {author.get('bio', '')}, "
            f"interests: {', '.join(author.get('interests', []))}, "
            f"learning focus: {author.get('learning_focus', '')}\n\n"
            f"Available categories:\n{category_hint}\n\n"
            "Return ONLY valid JSON with this exact structure:\n"
            '{\n  "title": "...",\n  "content": "... full markdown, minimum 600 words ...",\n'
            '  "tags": ["tag1", "tag2"],\n  "category_id": "uuid-string"\n}\n'
            "No markdown fences, no preamble. The content field must be at least 600 words."
        )

        user_prompt = (
            f"Write a blog post about: {state.get('topic', '')}\n\n"
            f"Research brief:\n{research}\n\n"
            f"Previous posts by this author (for continuity):\n{past_titles}"
        )

        groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

        generation = langfuse.generation(
            trace_id=state["langfuse_trace_id"],
            parent_observation_id=span.id,
            name="writer_draft_generation",
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

        raw_text = response.choices[0].message.content or ""
        generation.update(
            output=raw_text,
            usage={
                "input": response.usage.prompt_tokens if response.usage else 0,
                "output": response.usage.completion_tokens if response.usage else 0,
            },
        )

        try:
            parsed = json.loads(raw_text)
            title = parsed["title"]
            content = parsed["content"]
            tags = parsed.get("tags", [])
            category_id = parsed.get("category_id", "")
        except (json.JSONDecodeError, KeyError):
            retry_generation = langfuse.generation(
                trace_id=state["langfuse_trace_id"],
                parent_observation_id=span.id,
                name="writer_draft_retry",
                model=settings.GROQ_MODEL,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": raw_text},
                    {"role": "user",
                     "content": "Your response was not valid JSON. Reply with ONLY the JSON object, no markdown, no preamble."},
                ],
            )

            retry_response = await groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": raw_text},
                    {"role": "user",
                     "content": "Your response was not valid JSON. Reply with ONLY the JSON object, no markdown, no preamble."},
                ],
                response_format={"type": "json_object"},
            )
            retry_text = retry_response.choices[0].message.content or ""
            retry_generation.update(
                output=retry_text,
                usage={
                    "input": retry_response.usage.prompt_tokens if retry_response.usage else 0,
                    "output": retry_response.usage.completion_tokens if retry_response.usage else 0,
                },
            )
            parsed = json.loads(retry_text)
            title = parsed["title"]
            content = parsed["content"]
            tags = parsed.get("tags", [])
            category_id = parsed.get("category_id", "")

        known_ids = {c["id"] for c in category_list}
        if category_id not in known_ids and category_list:
            fallback = category_list[0]
            logger.warning(
                "LLM returned unknown category_id=%s — using first available: %s (%s)",
                category_id, fallback["name"], fallback["id"],
            )
            category_id = fallback["id"]

        span.update(status_message=f"draft_generated_{len(content)}_chars")
        span.end()
        return {
            "draft_title": title,
            "draft_content": content,
            "draft_tags": tags,
            "draft_category_id": category_id,
        }

    except Exception as exc:
        span.update(level="ERROR", status_message=str(exc))
        span.end()
        raise RuntimeError(f"writer_node failed: {exc}") from exc


_TONE_FALLBACK = (
    "Write in a clear, practical, developer-focused style. "
    "Use short paragraphs and concrete examples over abstract theory. "
    "Keep a direct, confident tone."
)
