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
from app.core.logging_config import get_logger, log_truncated

logger = get_logger("technical_agent")


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
    logger.info(f"Technical Agent Tool: Called with query=\"{query}\"")
    context = _rag_strategy.get_context(query)
    logger.info(f"Technical Agent Tool: Returned {len(context)} chars of technical content")
    log_truncated(logger, context, prefix="Technical Agent Tool: Content preview: ", max_chars=200)
    return context


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
            "MANDATORY TOOL USAGE - YOU CANNOT PROCEED WITHOUT CALLING THE TOOL:\n"
            "1. You MUST call search_technical_docs tool FIRST for EVERY question - NO EXCEPTIONS.\n"
            "2. You do NOT have access to technical documentation in your training data.\n"
            "3. If you try to answer without calling the tool, you will provide incorrect or generic information.\n"
            "4. The tool is the ONLY way to access accurate technical information.\n"
            "5. NEVER say 'I couldn't find' or 'I don't have access' - you MUST call the tool FIRST.\n\n"
            "AFTER CALLING THE TOOL:\n"
            "1. Read the retrieved documentation carefully.\n"
            "2. Extract the relevant information that answers the user's question.\n"
            "3. Provide a comprehensive answer that includes:\n"
            "   - All relevant error types, codes, and their solutions\n"
            "   - Step-by-step troubleshooting instructions\n"
            "   - Code examples and snippets when available\n"
            "   - Specific causes and fixes for each issue\n"
            "4. Format responses with clear sections, numbered steps, code blocks, and examples.\n"
            "5. Include enough detail to be useful - provide actual steps and solutions.\n"
            "6. If the documentation doesn't contain the answer, be honest and suggest contacting support.\n\n"
            "EXAMPLE WORKFLOW for 'How do I fix API errors?':\n"
            "Step 1: CALL search_technical_docs(query='API errors')\n"
            "Step 2: Read the retrieved documentation\n"
            "Step 3: Provide answer including:\n"
            "   - All error types found (401, 429, 500, etc.)\n"
            "   - Causes for each error\n"
            "   - Specific solutions and steps\n"
            "   - Code examples if available\n"
            "   - Complete troubleshooting guide\n\n"
            "REMEMBER: Tool call FIRST, then answer based on what the tool returns."
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


