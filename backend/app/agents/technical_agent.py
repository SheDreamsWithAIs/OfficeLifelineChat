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
            "explain how to use features, and provide helpful guidance based on "
            "the technical documentation.\n\n"
            "CRITICAL RULES:\n"
            "1. You MUST ALWAYS call the search_technical_docs tool FIRST before answering any question.\n"
            "2. NEVER answer technical questions without using the tool - you do not have technical information in your training data.\n"
            "3. After retrieving the documentation, provide a helpful answer that includes the relevant details from the documentation.\n"
            "4. Include the key steps, code examples, error codes, and solutions that are relevant to the user's question.\n"
            "5. Format responses with clear sections, numbered steps, code blocks, and examples when appropriate.\n"
            "6. Include enough detail to be useful - provide actual steps and solutions, not just 'check the documentation'.\n"
            "7. Be thorough but focused - include what's relevant to answer the question well.\n"
            "8. If the documentation doesn't contain the answer, be honest about it and suggest contacting support.\n\n"
            "Example: If asked 'How do I fix API errors?', you MUST:\n"
            "- Call search_technical_docs tool\n"
            "- Include the common error types found in the documentation (401, 429, 500, etc.)\n"
            "- Include the causes, solutions, and steps for each error type\n"
            "- Include code examples and specific troubleshooting steps when available\n"
            "- Provide a complete, well-organized answer that helps the user fix their issues."
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
    
    For development: recreates the agent each time to pick up prompt changes.
    In production, you might want to cache this.
    
    Returns:
        Technical agent instance
    """
    global _technical_agent
    # Recreate for development to pick up prompt changes
    # In production, you might want: if _technical_agent is None:
    _technical_agent = create_technical_agent()
    return _technical_agent


