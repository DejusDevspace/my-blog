"""LangGraph pipeline definition for the d3jusdevspace agent."""

from langgraph.graph import END, START, StateGraph

from app.devspace_agents.nodes.context_node import context_node
from app.devspace_agents.nodes.orchestrator_node import orchestrator_node
from app.devspace_agents.nodes.research_node import research_node
from app.devspace_agents.nodes.tone_node import tone_node
from app.devspace_agents.nodes.writer_node import writer_node
from app.devspace_agents.pipeline.state import AgentState


def build_pipeline() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("research", research_node)
    graph.add_node("context", context_node)
    graph.add_node("tone", tone_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "research")
    graph.add_edge("orchestrator", "context")
    graph.add_edge("orchestrator", "tone")
    graph.add_edge("research", "writer")
    graph.add_edge("context", "writer")
    graph.add_edge("tone", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


pipeline = build_pipeline()
