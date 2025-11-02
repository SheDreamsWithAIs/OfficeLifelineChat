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
    - Pricing and plans (e.g., "what are your pricing plans", "how much does it cost", "pricing")
    - Invoice questions (e.g., "invoice", "billing statement")
    - Payment methods (e.g., "how do I pay", "payment options")
    - Billing cycles (e.g., "when am I billed", "billing frequency")
    - Refunds and cancellations (e.g., "refund", "cancel subscription")
    - Account billing history (e.g., "billing history", "past invoices")
    - Subscription management (e.g., "change plan", "upgrade", "downgrade")
    
    Keywords that indicate billing: pricing, price, cost, plan, payment, invoice, billing, subscription, refund, cancel, upgrade, downgrade
    
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
    Handle EXPLICIT requests for jokes, dad jokes, or humor.
    
    Use this tool ONLY when users EXPLICITLY request humor:
    - Directly ask for a joke: "tell me a joke", "give me a dad joke", "make me laugh", "tell me something funny"
    - Use humor-related keywords: "joke", "funny", "humor", "dad joke", "something funny", "cheer me up"
    - Explicitly request emotional support through comedy: "I need a joke", "cheer me up with a joke"
    
    Keywords that indicate joke requests: joke, jokes, funny, humor, humour, laugh, dad joke, cheer me up, make me laugh
    
    DO NOT use this tool for:
    - General questions even if user seems stressed (they might want actual help)
    - Technical, billing, or policy questions (route to appropriate specialist)
    - Questions that don't explicitly mention jokes or humor
    
    Args:
        query: User's EXPLICIT request for humor or joke
        
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
            "Your role is to analyze EACH user query independently and route it to the appropriate "
            "specialist agent by CALLING THE APPROPRIATE TOOL.\n\n"
            "Available specialist agents (TOOLS YOU MUST CALL):\n"
            "1. handle_policy_query - For policy, compliance, terms of service, privacy policy questions\n"
            "2. handle_technical_query - For technical support, API, troubleshooting, setup questions\n"
            "3. handle_billing_query - For billing, pricing, invoices, payment questions\n"
            "4. handle_dad_joke_request - ONLY for EXPLICIT requests for jokes, humor, or dad jokes\n\n"
            "CRITICAL ROUTING RULES:\n"
            "- You MUST ALWAYS call one of the tools above - NEVER respond without calling a tool\n"
            "- DO NOT say 'I have routed' or 'I will route' - just CALL the tool and return its response\n"
            "- Evaluate EACH query independently - do NOT assume the previous query determines the current one\n\n"
            "ROUTING DECISION LOGIC (in priority order):\n"
            "1. If query contains joke/humor keywords ('joke', 'funny', 'humor', 'laugh', 'dad joke') → handle_dad_joke_request\n"
            "2. If query contains billing keywords ('pricing', 'price', 'cost', 'plan', 'payment', 'invoice', 'billing', 'subscription', 'refund', 'cancel') → handle_billing_query\n"
            "3. If query contains policy keywords ('privacy policy', 'terms of service', 'policy', 'compliance', 'terms') → handle_policy_query\n"
            "4. If query contains technical keywords ('API', 'error', 'bug', 'troubleshoot', 'fix', 'how to', 'technical', 'setup', 'configuration') → handle_technical_query\n"
            "5. For general questions without specific keywords, use handle_technical_query as default\n\n"
            "EXAMPLES:\n"
            "- 'tell me a joke' → handle_dad_joke_request\n"
            "- 'what are your pricing plans' → handle_billing_query\n"
            "- 'what is your privacy policy' → handle_policy_query\n"
            "- 'how do I fix API errors' → handle_technical_query\n\n"
            "- Call ONLY ONE tool per query\n"
            "- After calling a tool, return the tool's response DIRECTLY to the user as-is\n"
            "- DO NOT add your own commentary - just return what the tool returned\n"
            "- Be precise: each new query should be evaluated on its own merits, not based on conversation history"
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
    
    For development: recreates the agent each time to pick up prompt changes.
    In production, you might want to cache this.
    
    Returns:
        Orchestrator agent instance
    """
    global _orchestrator
    # Recreate for development to pick up prompt/routing changes
    # In production, you might want: if _orchestrator is None:
    _orchestrator = create_orchestrator()
    return _orchestrator

