"""
Technical Support Agent - Pure RAG Strategy.

This agent uses RAG (Retrieval-Augmented Generation) to retrieve relevant
technical documentation chunks and provide accurate technical support.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/agents
"""

from langchain.agents import create_agent
from langchain.tools import tool
from app.llm.providers import get_generation_model
from app.retrieval.rag_strategy import RAGStrategy
from app.core.checkpointing import get_or_create_checkpointer


# Initialize RAG strategy for technical documents
_rag_strategy = RAGStrategy(collection_name="technical_documents", k=3)


@tool
def search_technical_docs(query: str) -> str:
    """
    Search technical documentation including API guides, troubleshooting, and setup instructions.
    
    Use this tool when users ask about:
    - API errors and troubleshooting
    - Technical setup and configuration
    - How to use specific features
    - Integration guides
    - Technical specifications
    - Error messages and solutions
    
    Args:
        query: User's technical question
        
    Returns:
        Relevant technical documentation chunks from the knowledge base
    """
    return _rag_strategy.get_context(query)


def create_technical_agent():
    """
    Create the Technical Support agent.
    
    Returns:
        LangGraph agent configured for technical queries
    """
    model = get_generation_model()
    checkpointer = get_or_create_checkpointer()
    
    agent = create_agent(
        model=model,
        tools=[search_technical_docs],
        system_prompt=(
            "You are a Technical Support specialist. "
            "Your role is to help users troubleshoot technical issues, "
            "explain how to use features, and provide guidance based on "
            "the technical documentation.\n\n"
            "IMPORTANT: Always use the search_technical_docs tool to retrieve "
            "relevant technical information before answering questions. "
            "Provide clear, step-by-step solutions when possible. "
            "If the documentation doesn't contain the answer, be honest about it "
            "and suggest contacting support for further assistance."
        ),
        checkpointer=checkpointer,
        name="technical_support_agent"
    )
    
    return agent


# Global agent instance
_technical_agent = None


def get_technical_agent():
    """
    Get or create the global technical agent instance.
    
    Returns:
        Technical agent instance
    """
    global _technical_agent
    if _technical_agent is None:
        _technical_agent = create_technical_agent()
    return _technical_agent

