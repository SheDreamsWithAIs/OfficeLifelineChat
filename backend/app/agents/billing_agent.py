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
from app.agents.models import BillingResponse


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
        response_format=BillingResponse,  # Structured output for consistent formatting
        system_prompt=(
            "You are a Billing Support specialist. "
            "Your role is to help users with billing questions including pricing, "
            "invoices, payment methods, refunds, and account billing.\n\n"
            "CRITICAL RULES - FOLLOW THESE EXACTLY:\n"
            "1. You MUST ALWAYS call the search_billing_info tool FIRST before generating your structured response.\n"
            "2. NEVER generate a response without calling the tool - you do not have billing information in your training data.\n"
            "3. AFTER calling search_billing_info and receiving the billing content, THEN generate your structured response:\n"
            "   - friendly_response: A warm, conversational 1-2 sentence introduction\n"
            "   - billing_description: Detailed billing information with all relevant details from the documentation.\n"
            "     Include pricing, plans, payment methods, billing cycles, refunds, etc. Format with proper markdown:\n"
            "     * Use headings (##) for major sections\n"
            "     * Use bullet points (-) for lists, each on its own line\n"
            "     * Use numbered lists (1., 2., 3.) for step-by-step instructions\n"
            "   - plans: List of pricing plans with details if applicable (as dictionaries or strings)\n"
            "   - payment_info: Payment methods and billing cycle information if applicable\n"
            "4. The billing_description field MUST contain substantial detail from the documentation.\n"
            "5. Format billing_description with clear sections and proper markdown formatting.\n"
            "6. Ensure bullet points are properly formatted: each bullet on its own line with a blank line before the list.\n"
            "7. If the documentation doesn't contain the answer, set billing_description to explain this clearly.\n\n"
            "WORKFLOW:\n"
            "Step 1: Call search_billing_info tool with the user's query\n"
            "Step 2: Read the returned billing content carefully\n"
            "Step 3: Generate structured response with friendly_response and detailed billing_description\n"
            "Step 4: Extract plans and payment_info into separate fields if applicable"
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

