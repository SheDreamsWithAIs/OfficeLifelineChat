"""
Model selection logic for multi-LLM strategy.

LangChain Version: v1.0+
"""

from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock

from app.llm.providers import (
    get_openai_model,
    get_bedrock_model,
    get_routing_model,
    get_generation_model
)


# Model selection strategy constants
class ModelStrategy:
    """Model selection strategy constants."""
    
    ROUTING = "routing"  # Fast, cost-effective model for routing decisions
    GENERATION = "generation"  # High-quality model for response generation


def get_model_for_purpose(purpose: str, streaming: bool = False):
    """
    Get appropriate model based on purpose.
    
    Args:
        purpose: Either 'routing' or 'generation'
        streaming: Enable streaming responses
        
    Returns:
        ChatOpenAI or ChatBedrock model instance
    """
    if purpose == ModelStrategy.ROUTING:
        return get_routing_model()
    elif purpose == ModelStrategy.GENERATION:
        return get_generation_model()
    else:
        raise ValueError(f"Unknown purpose: {purpose}. Use 'routing' or 'generation'.")


def get_routing_model_instance() -> ChatBedrock:
    """
    Get routing model instance (Bedrock - fast/cheap).
    
    Returns:
        ChatBedrock model configured for routing
    """
    return get_routing_model()


def get_generation_model_instance() -> ChatOpenAI:
    """
    Get generation model instance (OpenAI - high quality).
    
    Returns:
        ChatOpenAI model configured for generation
    """
    return get_generation_model()


# Model configuration presets
MODEL_CONFIGS = {
    "routing": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "temperature": 0.3,
        "description": "Fast, cost-effective model for routing queries to agents"
    },
    "generation": {
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "temperature": 0.7,
        "description": "High-quality model for generating agent responses"
    }
}

