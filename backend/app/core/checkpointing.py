"""
Checkpointing setup for LangGraph conversation persistence.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langgraph/checkpoints
"""

from langgraph.checkpoint.memory import MemorySaver
from typing import Protocol


class CheckpointSaver(Protocol):
    """Protocol for checkpoint saver implementations."""
    pass


def get_checkpointer() -> MemorySaver:
    """
    Get checkpoint saver for conversation persistence.
    
    Uses MemorySaver for development. For production, switch to
    database-backed checkpointers (PostgreSQL, Redis).
    
    Returns:
        MemorySaver: Checkpoint saver instance
    """
    return MemorySaver()


# Global checkpointer instance
_checkpointer: MemorySaver | None = None


def get_or_create_checkpointer() -> MemorySaver:
    """
    Get or create global checkpointer instance.
    
    Returns:
        MemorySaver: Shared checkpointer instance
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = get_checkpointer()
    return _checkpointer

