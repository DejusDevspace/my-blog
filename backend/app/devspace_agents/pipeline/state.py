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
    last_generated_topic: str | None

    research_results: list[dict]
    research_summary: str
    research_key_concepts: list[str]
    research_angles: list[str]
    research_notable_sources: list[dict]

    author_context: dict
    relevant_past_posts: list[dict]

    tone_profile: str
    tone_opening_pattern: str
    tone_humour_style: str
    tone_technical_depth: str
    tone_structure_notes: str
    tone_avoid: list[str]

    draft_title: str
    draft_content: str
    draft_tags: list[str]
    draft_category_id: str

    output_post_id: str
    run_status: str
    error_message: str
