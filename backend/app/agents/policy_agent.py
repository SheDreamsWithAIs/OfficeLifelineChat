"""
Policy & Compliance Agent - Pure CAG Strategy.

This agent uses CAG (Cached-Augmented Generation) to provide fast,
consistent answers based on static policy documents.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/agents
"""

from langchain.agents import create_agent
from langchain.tools import tool
from app.llm.providers import get_generation_model
from app.retrieval.cag_strategy import CAGStrategy
from app.core.checkpointing import get_or_create_checkpointer
from app.agents.models import PolicyResponse


# Initialize CAG strategy for policy documents
_cag_strategy = CAGStrategy()


@tool
def get_policy_documents(query: str = "") -> str:
    """
    Get policy documents including Terms of Service, Privacy Policy, and Compliance guidelines.
    
    Use this tool when users ask about:
    - Privacy policies
    - Terms of service
    - Compliance requirements
    - Data handling policies
    - User rights and responsibilities
    
    Args:
        query: User's question (optional - returns all documents)
        
    Returns:
        Full content of all policy documents
    """
    return _cag_strategy.get_context(query)


def create_policy_agent():
    """
    Create the Policy & Compliance agent.
    
    Returns:
        LangGraph agent configured for policy queries
    """
    model = get_generation_model()
    checkpointer = get_or_create_checkpointer()
    
    agent = create_agent(
        model=model,
        tools=[get_policy_documents],
        response_format=PolicyResponse,  # Structured output for consistent formatting
        system_prompt=(
            "You are a Policy & Compliance specialist. "
            "Your role is to provide accurate, helpful answers about company policies, "
            "terms of service, privacy policies, and compliance requirements.\n\n"
            "CRITICAL RULES - FOLLOW THESE EXACTLY:\n"
            "1. You MUST ALWAYS call the get_policy_documents tool FIRST before generating your structured response.\n"
            "2. NEVER generate a response without calling the tool - you do not have policy information in your training data.\n"
            "3. AFTER calling get_policy_documents and receiving the policy content, THEN generate your structured response:\n"
            "   - friendly_response: A warm, conversational 1-2 sentence introduction (e.g., 'Here's our privacy policy!')\n"
            "   - policy_description: MUST include ALL the key information from the retrieved documents. "
            "     Extract and summarize the actual policy content. Include specific details about:\n"
            "     * What information is collected\n"
            "     * How information is used\n"
            "     * Information sharing practices\n"
            "     * Security measures\n"
            "     * User rights\n"
            "     Format with proper markdown bullet points (each bullet on its own line).\n"
            "   - key_points: List of 3-5 main sections or key points from the policy\n"
            "   - contact_info: Contact information if mentioned in the documents\n"
            "4. The policy_description field MUST contain substantial detail from the documents - "
            "DO NOT just say 'refer to the document' or give a brief summary.\n"
            "5. Format policy_description with clear sections and markdown bullet points.\n"
            "6. Ensure bullet points are properly formatted: each bullet on its own line with a blank line before the list.\n"
            "7. If the documents don't contain the answer, set policy_description to explain this clearly.\n\n"
            "WORKFLOW:\n"
            "Step 1: Call get_policy_documents tool with the user's query\n"
            "Step 2: Read the returned policy content carefully\n"
            "Step 3: Generate structured response with friendly_response and detailed policy_description\n"
            "Step 4: Include key_points extracted from the actual document content"
        ),
        checkpointer=checkpointer,
        name="policy_compliance_agent"
    )
    
    return agent


# Global agent instance
_policy_agent = None


def get_policy_agent():
    """
    Get or create the global policy agent instance.
    
    Returns:
        Policy agent instance
    """
    global _policy_agent
    # Always recreate to pick up prompt changes (or use a cache invalidation strategy)
    # For development, recreate each time; for production, cache and invalidate on config change
    _policy_agent = create_policy_agent()
    return _policy_agent


