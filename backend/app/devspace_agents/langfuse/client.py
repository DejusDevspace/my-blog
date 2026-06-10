"""LangFuse client — singleton initialisation for pipeline observability.

LangFuse v4 API: uses `start_observation(trace_context=..., as_type=...)`
instead of the old `trace()` / `span()` / `generation()` methods.

Usage pattern:

    from app.devspace_agents.langfuse.client import langfuse

    # Runner creates a root span (which also creates the trace):
    root = langfuse.start_observation(
        trace_context={"id": run_id, "name": "pipeline", "user_id": owner_id, "tags": [...]},
        name="agent_pipeline", as_type="span",
        input={"owner_id": owner_id, "triggered_by": triggered_by},
    )
    root.update(output={"status": "completed", "post_id": ..., "topic": ...})

    # Log an LLM generation inside the span:
    gen = span.start_observation(
        name="research_summarise", as_type="generation",
        model=settings.GROQ_MODEL,
        input=[...],
    )
    gen.update(output=response_text, usage_details={"input": n, "output": n})
    gen.end()

    # Log a non-LLM event:
    span.create_event(name="tavily_search", input=..., output=...)

    span.end()
    root.end()
"""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


def _build_client():
    """Return a real LangFuse client or a no-op stub."""
    if settings.LANGFUSE_PUBLIC_KEY:
        from langfuse import Langfuse

        logger.info("LangFuse tracing enabled.")
        return Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
    logger.warning("LANGFUSE_PUBLIC_KEY not set — tracing disabled (no-op mode).")
    return _NoOpLangfuse()


class _NoOpSpan:
    """No-op span matching LangfuseSpan interface when tracing is disabled."""

    id: str = "noop"

    def update(self, **kwargs) -> None:
        pass

    def end(self, **kwargs) -> None:
        pass

    def start_observation(self, **kwargs) -> "_NoOpSpan":
        return _NoOpSpan()

    def create_event(self, **kwargs) -> None:
        pass


class _NoOpLangfuse:
    """Drop-in stub matching the Langfuse v4 SDK interface."""

    def start_observation(self, **kwargs) -> _NoOpSpan:
        return _NoOpSpan()

    def flush(self) -> None:
        pass


# Module-level singleton — imported by pipeline_runner and all nodes.
langfuse = _build_client()
