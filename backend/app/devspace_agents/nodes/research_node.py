"""Research node — web search and source summarization."""

import json
import logging

from groq import AsyncGroq
from tavily import TavilyClient

from app.config import settings
from app.devspace_agents.langfuse.client import langfuse
from app.devspace_agents.pipeline.state import AgentState

logger = logging.getLogger(__name__)


async def research_node(state: AgentState) -> dict:
    span = langfuse.span(
        trace_id=state["langfuse_trace_id"],
        name="research_node",
    )
    try:
        if not settings.TAVILY_API_KEY:
            logger.warning("TAVILY_API_KEY not set — skipping research.")
            span.update(status_message="tavily_skipped_no_key")
            span.end()
            return {"research_results": [], "research_summary": ""}

        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query=state["topic"],
            max_results=5,
            search_depth="advanced",
        )
        raw_results = results.get("results", [])

        langfuse.event(
            trace_id=state["langfuse_trace_id"],
            parent_observation_id=span.id,
            name="tavily_search",
            input={"query": state["topic"], "max_results": 5},
            output={"result_count": len(raw_results)},
        )

        if not raw_results:
            span.update(status_message="no_sources_found")
            span.end()
            return {"research_results": [], "research_summary": ""}

        sources_text = "\n\n".join(
            f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')[:2000]}"
            for r in raw_results
        )

        system_prompt = (
            "You are a research summarisation assistant. "
            "Given web search results about a topic, produce a focused ~300-word "
            "research brief that captures key facts, data, and perspectives. "
            "Return ONLY valid JSON: {\"summary\": \"...\"} No markdown, no preamble."
        )
        user_prompt = (
            f"Topic: {state['topic']}\n\n"
            f"Search Results:\n{sources_text}"
        )

        groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

        generation = langfuse.generation(
            trace_id=state["langfuse_trace_id"],
            parent_observation_id=span.id,
            name="research_summarise",
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
            summary = parsed["summary"]
        except (json.JSONDecodeError, KeyError):
            summary = response_text

        span.update(status_message=f"{len(raw_results)}_sources_found")
        span.end()
        return {
            "research_results": [
                {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", ""), "score": r.get("score", 0)}
                for r in raw_results
            ],
            "research_summary": summary,
        }

    except Exception as exc:
        span.update(level="ERROR", status_message=str(exc))
        span.end()
        raise RuntimeError(f"research_node failed: {exc}") from exc
