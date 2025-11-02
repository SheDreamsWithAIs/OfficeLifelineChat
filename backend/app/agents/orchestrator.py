"""
Orchestrator Agent - Supervisor that routes queries to specialized worker agents.

Uses the supervisor pattern (tool calling) where worker agents are wrapped as tools.
The orchestrator uses Bedrock for fast, cost-effective routing decisions.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/multi-agent
"""

from langchain.agents import create_agent
from langchain.tools import tool
from app.llm.providers import get_routing_model  # Smaller model for routing
from app.agents.policy_agent import get_policy_agent
from app.agents.technical_agent import get_technical_agent
from app.agents.billing_agent import get_billing_agent
from app.agents.dad_joke_agent import get_dad_joke_agent
from app.core.checkpointing import get_or_create_checkpointer


# Wrap worker agents as tools for the supervisor
@tool
def handle_policy_query(query: str) -> str:
    """
    Handle policy, compliance, terms of service, and privacy policy questions.
    
    Use this tool when users ask about:
    - Privacy policies
    - Terms of service
    - Compliance requirements
    - Data handling policies
    - User rights and responsibilities
    - Legal or policy-related questions
    
    Args:
        query: User's policy-related question
        
    Returns:
        Complete answer from the policy specialist agent
    """
    policy_agent = get_policy_agent()
    result = policy_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    # Return the final message content from the agent
    return result["messages"][-1].content


@tool
def handle_technical_query(query: str) -> str:
    """
    Handle technical support, API, troubleshooting, and setup questions.
    
    Use this tool when users ask about:
    - API errors and troubleshooting
    - Technical setup and configuration
    - How to use specific features
    - Integration guides
    - Technical specifications
    - Error messages and solutions
    - Technical documentation
    
    Args:
        query: User's technical question
        
    Returns:
        Complete answer from the technical support specialist agent
    """
    technical_agent = get_technical_agent()
    result = technical_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    # Return the final message content from the agent
    return result["messages"][-1].content


@tool
def handle_billing_query(query: str) -> str:
    """
    Handle billing, pricing, invoices, and payment questions.
    
    Use this tool when users ask about:
    - Pricing and plans
    - Invoice questions
    - Payment methods
    - Billing cycles
    - Refunds and cancellations
    - Account billing history
    - Subscription management
    
    Args:
        query: User's billing question
        
    Returns:
        Complete answer from the billing support specialist agent
    """
    billing_agent = get_billing_agent()
    result = billing_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    # Return the final message content from the agent
    return result["messages"][-1].content


@tool
def handle_dad_joke_request(query: str) -> str:
    """
    Handle requests for jokes, dad jokes, humor, or emotional support through comedy.
    
    Use this tool when users:
    - Ask for a joke, dad joke, or something funny
    - Request humor or need a mood lift
    - Express stress, overwhelm, or need for levity
    - Say things like "tell me a joke", "I need something funny", "make me laugh"
    - Seem like they need emotional support through humor
    
    Args:
        query: User's request for humor or joke
        
    Returns:
        A contextually relevant dad joke from the dad joke specialist agent
    """
    dad_joke_agent = get_dad_joke_agent()
    result = dad_joke_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    # Return the final message content from the agent
    return result["messages"][-1].content


def create_orchestrator():
    """
    Create the orchestrator agent (supervisor).
    
    Uses a smaller/faster model (gpt-3.5-turbo) for routing decisions.
    Worker agents use gpt-4o-mini for higher quality generation.
    This maintains multi-model strategy: routing (smaller) vs generation (higher quality).
    
    Returns:
        LangGraph agent configured as supervisor/router
    """
    model = get_routing_model()  # Smaller model for fast routing
    checkpointer = get_or_create_checkpointer()
    
    agent = create_agent(
        model=model,
        tools=[handle_policy_query, handle_technical_query, handle_billing_query, handle_dad_joke_request],
        system_prompt=(
            "You are an intelligent customer service orchestrator. "
            "Your role is to analyze user queries and route them to the appropriate "
            "specialist agent.\n\n"
            "Available specialist agents:\n"
            "1. handle_policy_query - For policy, compliance, terms of service, privacy policy questions\n"
            "2. handle_technical_query - For technical support, API, troubleshooting, setup questions\n"
            "3. handle_billing_query - For billing, pricing, invoices, payment questions\n"
            "4. handle_dad_joke_request - For jokes, humor, emotional support, or when users need a mood lift\n\n"
            "ROUTING RULES:\n"
            "- If the user asks for a joke, dad joke, humor, or something funny → ALWAYS use handle_dad_joke_request\n"
            "- If the user seems stressed, overwhelmed, or needs emotional support → use handle_dad_joke_request\n"
            "- Keywords that indicate joke requests: 'joke', 'funny', 'humor', 'dad joke', 'make me laugh', 'something funny'\n"
            "- For all other queries, analyze the content and route to the appropriate specialist\n"
            "- Call ONLY ONE agent per query\n"
            "- Return the agent's response directly to the user\n"
            "- Be concise in your routing decisions"
        ),
        checkpointer=checkpointer,
        name="orchestrator_agent"
    )
    
    return agent


# Global orchestrator instance
_orchestrator = None


def get_orchestrator():
    """
    Get or create the global orchestrator instance.
    
    Returns:
        Orchestrator agent instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = create_orchestrator()
    return _orchestrator

