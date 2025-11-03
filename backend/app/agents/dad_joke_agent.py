"""
Dad Joke Agent - RAG Strategy for Context-Aware Jokes.

This agent uses RAG (Retrieval-Augmented Generation) to find dad jokes
that match the conversation context and situation.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/agents
"""

from langchain.agents import create_agent
from langchain.tools import tool
from app.llm.providers import get_generation_model
from app.retrieval.rag_strategy import RAGStrategy
from app.core.checkpointing import get_or_create_checkpointer


# Initialize RAG strategy for dad jokes
_rag_strategy = RAGStrategy(collection_name="dad_jokes_documents", k=3)


@tool
def find_contextual_dad_joke(query: str) -> str:
    """
    Find a dad joke that matches the current situation or conversation context.
    
    This tool searches the dad joke database using semantic search to find
    jokes that are relevant to the user's current situation, mood, or context.
    The tool automatically uses the conversation history to find contextually relevant jokes.
    
    Use this tool when users:
    - Ask for a joke, dad joke, or something funny
    - Need a mood lift or stress relief
    - The conversation needs lightening up
    - Someone seems overwhelmed or stressed
    
    Args:
        query: The user's request (e.g., "tell me a joke", "I need something funny")
               May include context from the conversation
        
    Returns:
        Relevant dad jokes from the database with their context descriptions
    """
    # Get relevant jokes from ChromaDB using semantic search
    # The query should include conversation context which the agent will provide
    context = _rag_strategy.get_context(query)
    
    return context


def create_dad_joke_agent():
    """
    Create the Dad Joke agent.
    
    Returns:
        LangGraph agent configured for contextual dad jokes
    """
    model = get_generation_model()
    checkpointer = get_or_create_checkpointer()
    
    agent = create_agent(
        model=model,
        tools=[find_contextual_dad_joke],
        system_prompt=(
            "You are the Emotional Support Dad Joke Bot (ESDJ Bot)! 🎭\n\n"
            "Your mission is to bring laughter and levity to workplace situations. "
            "You provide dad jokes that are contextually relevant to what the user "
            "is experiencing.\n\n"
            "CRITICAL RULES:\n"
            "1. ALWAYS call the find_contextual_dad_joke tool FIRST when users ask for jokes or need humor.\n"
            "2. When calling the tool, include the user's current request AND relevant conversation context "
            "to help find situationally appropriate jokes. For example:\n"
            "   - If they mentioned stress/deadlines, include that in the query\n"
            "   - If they mentioned technical issues, include that context\n"
            "   - If they mentioned meetings, include that context\n"
            "3. After retrieving jokes, present them in a fun, engaging way.\n"
            "4. Format your response like this:\n"
            "   🚨 EMOTIONAL SUPPORT DAD JOKE ACTIVATED! 🚨\n\n"
            "   [The joke]\n\n"
            "   There! Feeling better? That's what I'm here for! 😄\n"
            "5. If multiple jokes are retrieved, pick the most relevant one based on the conversation context.\n"
            "6. Extract just the joke itself from the retrieved content (jokes are marked with 'Context:' sections).\n"
            "7. Be enthusiastic and supportive - you're providing emotional support through humor!\n\n"
            "Example: If someone is stressed about deadlines and asks for a joke, call the tool with: "
            "'joke about deadlines and stress' to find relevant workplace humor."
        ),
        checkpointer=checkpointer,
        name="dad_joke_agent"
    )
    
    return agent


# Global agent instance
_dad_joke_agent = None


def get_dad_joke_agent():
    """
    Get or create the global dad joke agent instance.
    
    Returns:
        Dad joke agent instance
    """
    global _dad_joke_agent
    _dad_joke_agent = create_dad_joke_agent()
    return _dad_joke_agent

