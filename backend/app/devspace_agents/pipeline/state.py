"""Shared state schema for the d3jusdevspace agent pipeline.

This TypedDict is passed between every node in the LangGraph graph.
Each node reads from it and returns a partial dict to merge back in.
Fields are intentionally broad so every node can read what it needs
without tight coupling between nodes.
"""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Mutable state object threaded through the LangGraph pipeline."""

    owner_id: str
    triggered_by: str
    langfuse_trace_id: str
    langfuse_root_span_id: str

    topic: str
    topic_rationale: str

    research_results: list[dict]
    research_summary: str

    author_context: dict
    relevant_past_posts: list[dict]

    tone_profile: str

    draft_title: str
    draft_content: str
    draft_tags: list[str]
    draft_category_id: str

    output_post_id: str
    run_status: str
    error_message: str
