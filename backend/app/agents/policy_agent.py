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
            "CRITICAL RULES:\n"
            "1. You MUST ALWAYS call the get_policy_documents tool FIRST before answering any question.\n"
            "2. NEVER answer policy questions without using the tool - you do not have policy information in your training data.\n"
            "3. After retrieving the documents, structure your response:\n"
            "   - friendly_response: A warm, conversational 1-2 sentence introduction\n"
            "   - policy_description: Detailed explanation with all key information, formatted with proper markdown lists\n"
            "   - key_points: List of main sections or points (if applicable)\n"
            "   - contact_info: Contact information if relevant\n"
            "4. Include specific information that directly answers the user's question - be thorough but focused.\n"
            "5. Extract and share the relevant information from the documents - do NOT just say 'refer to the document'.\n"
            "6. Format policy_description with clear sections, bullet points (using markdown - format), or numbered lists.\n"
            "7. Ensure bullet points are properly formatted: each bullet on its own line with a blank line before the list.\n"
            "8. Include enough detail to be useful, but keep it readable and well-organized.\n"
            "9. If the documents don't contain the answer, say so clearly.\n\n"
            "Example: If asked 'What is your privacy policy?', you MUST:\n"
            "- Call get_policy_documents tool\n"
            "- Read the privacy policy content\n"
            "- Set friendly_response to a warm greeting\n"
            "- Set policy_description to include all key sections with proper markdown formatting\n"
            "- Set key_points to list the main sections\n"
            "- Provide a complete but well-organized answer based on the actual document content."
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


