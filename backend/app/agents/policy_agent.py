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
        system_prompt=(
            "You are a Policy & Compliance specialist. "
            "Your role is to provide accurate, complete answers about company policies, "
            "terms of service, privacy policies, and compliance requirements.\n\n"
            "IMPORTANT: Always use the get_policy_documents tool to retrieve policy information "
            "before answering questions. Return complete, accurate information based on the "
            "official policy documents. Be precise and reference specific policy sections when relevant."
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
    if _policy_agent is None:
        _policy_agent = create_policy_agent()
    return _policy_agent

