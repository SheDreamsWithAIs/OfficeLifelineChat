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
from app.agents.models import TechnicalResponse


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
        response_format=TechnicalResponse,  # Structured output for consistent formatting
        system_prompt=(
            "You are a Technical Support specialist. "
            "Your role is to help users troubleshoot technical issues, "
            "explain how to use features, and provide helpful guidance based on "
            "the technical documentation.\n\n"
            "CRITICAL RULES - FOLLOW THESE EXACTLY:\n"
            "1. You MUST ALWAYS call the search_technical_docs tool FIRST before generating your structured response.\n"
            "2. NEVER generate a response without calling the tool - you do not have technical information in your training data.\n"
            "3. AFTER calling search_technical_docs and receiving the documentation, THEN generate your structured response:\n"
            "   - friendly_response: A warm, conversational 1-2 sentence introduction\n"
            "   - technical_description: Detailed technical information with all relevant details from the documentation.\n"
            "     Include explanations, troubleshooting guidance, and solutions. Format with proper markdown:\n"
            "     * Use headings (##) for major sections\n"
            "     * Use bullet points (-) for lists, each on its own line\n"
            "     * Use numbered lists (1., 2., 3.) for step-by-step instructions\n"
            "     * Use code blocks (```) for code examples\n"
            "   - steps: List of step-by-step instructions if applicable (as separate strings)\n"
            "   - code_examples: List of code examples/snippets if applicable (as separate strings)\n"
            "   - error_codes: List of specific error codes and their solutions if applicable\n"
            "4. The technical_description field MUST contain substantial detail from the documentation.\n"
            "5. Format technical_description with clear sections and proper markdown formatting.\n"
            "6. Ensure bullet points are properly formatted: each bullet on its own line with a blank line before the list.\n"
            "7. If the documentation doesn't contain the answer, set technical_description to explain this clearly.\n\n"
            "WORKFLOW:\n"
            "Step 1: Call search_technical_docs tool with the user's query\n"
            "Step 2: Read the returned documentation carefully\n"
            "Step 3: Generate structured response with friendly_response and detailed technical_description\n"
            "Step 4: Extract steps, code_examples, and error_codes into separate fields if applicable"
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


