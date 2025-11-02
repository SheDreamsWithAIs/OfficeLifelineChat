"""
Billing Support Agent - Hybrid RAG/CAG Strategy.

This agent uses Hybrid RAG/CAG (Retrieval-Augmented Generation / Cached-Augmented Generation):
- First query: Performs RAG retrieval from ChromaDB
- Subsequent queries: Uses cached results from session state

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/agents
"""

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from app.llm.providers import get_generation_model
from app.retrieval.hybrid_strategy import HybridRAGCAGStrategy
from app.core.checkpointing import get_or_create_checkpointer


# Initialize Hybrid strategy for billing documents
_hybrid_strategy = HybridRAGCAGStrategy(collection_name="billing_documents", k=3)


@tool
def search_billing_info(query: str, runtime: ToolRuntime) -> str:
    """
    Search billing information including pricing, invoices, payment methods, and billing policies.
    
    Use this tool when users ask about:
    - Pricing and plans
    - Invoice questions
    - Payment methods
    - Billing cycles
    - Refunds and cancellations
    - Account billing history
    
    The first call will retrieve information from the knowledge base.
    Subsequent calls in the same conversation will use cached results for faster responses.
    
    Args:
        query: User's billing question
        runtime: Tool runtime (automatically injected) for accessing session state
        
    Returns:
        Relevant billing information from knowledge base or cache
    """
    # Get session cache from state
    state = runtime.state
    session_cache = state.get("session_cache", {})
    
    # Use hybrid strategy (RAG first call, cached subsequent calls)
    # This will update session_cache if it's the first call
    context = _hybrid_strategy.get_context(query, session_cache)
    
    # Update state (NOTE: State persistence via checkpointer may handle this)
    # For now, return the context string - caching may work through checkpointer
    state["session_cache"] = session_cache
    
    return context


def create_billing_agent():
    """
    Create the Billing Support agent.
    
    Returns:
        LangGraph agent configured for billing queries with session caching
    """
    model = get_generation_model()
    checkpointer = get_or_create_checkpointer()
    
    agent = create_agent(
        model=model,
        tools=[search_billing_info],
        system_prompt=(
            "You are a Billing Support specialist. "
            "Your role is to help users with billing questions including pricing, "
            "invoices, payment methods, refunds, and account billing.\n\n"
            "IMPORTANT: Always use the search_billing_info tool to retrieve "
            "relevant billing information before answering questions. "
            "The tool will automatically cache results for faster follow-up questions "
            "in the same conversation.\n\n"
            "Provide clear, accurate answers based on the billing documentation. "
            "If you cannot find the answer in the documentation, be honest and "
            "suggest contacting billing support for assistance."
        ),
        checkpointer=checkpointer,
        name="billing_support_agent"
    )
    
    return agent


# Global agent instance
_billing_agent = None


def get_billing_agent():
    """
    Get or create the global billing agent instance.
    
    Returns:
        Billing agent instance
    """
    global _billing_agent
    if _billing_agent is None:
        _billing_agent = create_billing_agent()
    return _billing_agent

