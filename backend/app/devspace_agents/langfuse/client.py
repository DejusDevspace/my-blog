"""LangFuse client — singleton initialisation for pipeline observability.

LangFuse is used to trace every agent pipeline run end-to-end:
  - One trace per pipeline run (tied to AgentRun.id)
  - One span per node (orchestrator, research, context, tone, writer)
  - One generation per LLM call (prompt, response, token counts, model)
  - One event for non-LLM operations (Tavily search, pgvector query)

Usage pattern in nodes:

    from app.devspace_agents.langfuse.client import langfuse

    # Open a span at the start of a node:
    span = langfuse.span(
        trace_id=state['langfuse_trace_id'],
        name="research_node",
    )

    # Log an LLM generation inside the span:
    generation = langfuse.generation(
        trace_id=state['langfuse_trace_id'],
        parent_observation_id=span.id,
        name="research_summarise",
        model=settings.GROQ_MODEL,
        input=[{"role": "system", "content": system_prompt},
               {"role": "user", "content": user_prompt}],
        output=response_text,
        usage={"input": prompt_tokens, "output": completion_tokens},
    )

    # Close the span when the node finishes:
    span.end()

The langfuse client is initialised once at import time from settings.
If LANGFUSE_PUBLIC_KEY is not set, a no-op stub is used so the pipeline
runs normally without tracing (useful in CI).
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
    """No-op span returned by _NoOpLangfuse when tracing is disabled."""

    id: str = "noop"

    def end(self, **kwargs) -> None:
        pass

    def update(self, **kwargs) -> None:
        pass


class _NoOpLangfuse:
    """Drop-in stub for the LangFuse client when keys are not configured.

    All methods return no-op objects so node code runs unchanged
    regardless of whether tracing is enabled.
    """

    def trace(self, **kwargs) -> _NoOpSpan:
        return _NoOpSpan()

    def span(self, **kwargs) -> _NoOpSpan:
        return _NoOpSpan()

    def generation(self, **kwargs) -> _NoOpSpan:
        return _NoOpSpan()

    def event(self, **kwargs) -> None:
        pass

    def flush(self) -> None:
        pass


# Module-level singleton — imported by pipeline_runner and all nodes.
langfuse = _build_client()
