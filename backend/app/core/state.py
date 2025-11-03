"""
LangGraph state definition for agent workflows.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langgraph
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Agent state schema for LangGraph workflows.
    
    This state is passed between nodes in the agent graph and maintains
    conversation context, retrieval cache, and agent routing information.
    """
    
    # Conversation messages (required for LangGraph)
    messages: Annotated[Sequence, add_messages]
    
    # Session cache for hybrid RAG/CAG strategy (billing agent)
    session_cache: dict
    
    # Current agent type handling the request
    current_agent: str
    
    # Query context from retrieval strategies
    retrieval_context: str
    
    # Thread ID for conversation persistence
    thread_id: str


def create_initial_state(thread_id: str = "default") -> AgentState:
    """
    Create initial agent state.
    
    Args:
        thread_id: Conversation thread identifier
        
    Returns:
        AgentState: Initialized state dictionary
    """
    return AgentState(
        messages=[],
        session_cache={},
        current_agent="",
        retrieval_context="",
        thread_id=thread_id
    )

