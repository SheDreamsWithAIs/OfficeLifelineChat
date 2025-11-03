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
from app.core.logging_config import get_logger, log_truncated

logger = get_logger("billing_agent")


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
    logger.info(f"Billing Agent Tool: Called with query=\"{query}\"")
    # Get session cache from state
    state = runtime.state
    session_cache = state.get("session_cache", {})
    
    # Use hybrid strategy (RAG first call, cached subsequent calls)
    # This will update session_cache if it's the first call
    context = _hybrid_strategy.get_context(query, session_cache)
    logger.info(f"Billing Agent Tool: Returned {len(context)} chars of billing content")
    log_truncated(logger, context, prefix="Billing Agent Tool: Content preview: ", max_chars=200)
    
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
            "MANDATORY TOOL USAGE - YOU CANNOT PROCEED WITHOUT CALLING THE TOOL:\n"
            "1. You MUST call search_billing_info tool FIRST for EVERY question - NO EXCEPTIONS.\n"
            "2. You do NOT have access to billing/pricing information in your training data.\n"
            "3. If you try to answer without calling the tool, you will provide incorrect or generic information.\n"
            "4. The tool is the ONLY way to access accurate billing information.\n"
            "5. NEVER say 'I recommend contacting billing support' without first calling the tool.\n"
            "6. NEVER provide generic answers - you MUST retrieve the actual pricing/plan information.\n\n"
            "AFTER CALLING THE TOOL:\n"
            "1. Read the retrieved billing information carefully.\n"
            "2. Extract ALL relevant details:\n"
            "   - Pricing plans and their costs\n"
            "   - Features included in each plan\n"
            "   - Payment methods and billing cycles\n"
            "   - Any other relevant billing details\n"
            "3. Present the information clearly and completely.\n"
            "4. Format responses with clear sections, pricing tables, and details.\n"
            "5. Include ALL pricing information found in the documentation.\n"
            "6. If the documentation doesn't contain the answer, be honest and suggest contacting billing support.\n\n"
            "EXAMPLE WORKFLOW for 'What are your pricing plans?':\n"
            "Step 1: CALL search_billing_info(query='pricing plans')\n"
            "Step 2: Read the retrieved documentation\n"
            "Step 3: Provide answer including:\n"
            "   - All pricing plans found\n"
            "   - Costs for each plan\n"
            "   - Features included\n"
            "   - Payment options\n"
            "   - Complete pricing information\n\n"
            "REMEMBER: Tool call FIRST, then answer based on what the tool returns. "
            "The tool will cache results for faster follow-up questions."
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
    
    For development: recreates the agent each time to pick up prompt changes.
    In production, you might want to cache this.
    
    Returns:
        Billing agent instance
    """
    global _billing_agent
    # Recreate for development to pick up prompt changes
    # In production, you might want: if _billing_agent is None:
    _billing_agent = create_billing_agent()
    return _billing_agent

