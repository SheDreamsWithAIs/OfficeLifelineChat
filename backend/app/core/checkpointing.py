"""
Checkpointing setup for LangGraph conversation persistence.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langgraph/checkpoints
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint import BaseCheckpointSaver


def get_checkpointer() -> BaseCheckpointSaver:
    """
    Get checkpoint saver for conversation persistence.
    
    Uses InMemorySaver for development. For production, switch to
    database-backed checkpointers (PostgreSQL, Redis).
    
    Returns:
        BaseCheckpointSaver: Checkpoint saver instance
    """
    return MemorySaver()


# Global checkpointer instance
_checkpointer: BaseCheckpointSaver | None = None


def get_or_create_checkpointer() -> BaseCheckpointSaver:
    """
    Get or create global checkpointer instance.
    
    Returns:
        BaseCheckpointSaver: Shared checkpointer instance
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = get_checkpointer()
    return _checkpointer

