"""
LLM provider initialization and configuration.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/models
"""

from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_aws import ChatBedrock

from app.core.config import get_settings


def get_openai_model(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.7,
    streaming: bool = False
) -> ChatOpenAI:
    """
    Get OpenAI chat model instance.
    
    Args:
        model_name: Model name (default: gpt-4o-mini for cost-effectiveness)
        temperature: Sampling temperature (0.0-2.0)
        streaming: Enable streaming responses
        
    Returns:
        ChatOpenAI: Configured OpenAI model
    """
    settings = get_settings()
    
    return ChatOpenAI(
        model=model_name,
        api_key=settings.openai_api_key,
        temperature=temperature,
        streaming=streaming
    )


def get_bedrock_model(
    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
    temperature: float = 0.7,
    streaming: bool = False
) -> ChatBedrock:
    """
    Get AWS Bedrock chat model instance.
    
    Uses API key authentication via AWS_BEDROCK_API_KEY environment variable.
    The API key is set in environment and boto3 will use it automatically.
    
    Args:
        model_id: Bedrock model ID (default: Claude 3 Haiku for fast/cheap routing)
        temperature: Sampling temperature (0.0-1.0)
        streaming: Enable streaming responses
        
    Returns:
        ChatBedrock: Configured Bedrock model
        
    Raises:
        ValueError: If Bedrock API key is not configured
    """
    settings = get_settings()
    bedrock_key = settings.get_bedrock_key()  # Validates key exists
    
    # Set API key in environment for boto3 to use
    # ChatBedrock uses boto3 under the hood, which reads from environment
    import os
    os.environ["AWS_BEDROCK_API_KEY"] = bedrock_key
    
    # Also set as AWS access key for boto3 compatibility
    # Note: Some Bedrock API key implementations may require this format
    os.environ["AWS_ACCESS_KEY_ID"] = bedrock_key
    
    return ChatBedrock(
        model_id=model_id,
        credentials_profile_name=None,  # Not using profile, using env vars
        region_name="us-east-1",  # Default region, can be configured
        model_kwargs={
            "temperature": temperature,
        },
        streaming=streaming
    )


def get_openai_embeddings(
    model_name: str = "text-embedding-3-small"
) -> OpenAIEmbeddings:
    """
    Get OpenAI embeddings model.
    
    Args:
        model_name: Embedding model name (default: text-embedding-3-small for cost-effectiveness)
        
    Returns:
        OpenAIEmbeddings: Configured embeddings model
    """
    settings = get_settings()
    
    return OpenAIEmbeddings(
        model=model_name,
        api_key=settings.openai_api_key
    )


# Convenience functions for specific use cases
def get_routing_model() -> ChatBedrock:
    """
    Get model for routing/orchestration (fast and cost-effective).
    
    Returns:
        ChatBedrock: Claude 3 Haiku model for routing decisions
    """
    return get_bedrock_model(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        temperature=0.3  # Lower temperature for more consistent routing
    )


def get_generation_model() -> ChatOpenAI:
    """
    Get model for response generation (high quality).
    
    Returns:
        ChatOpenAI: GPT-4o-mini model for generating responses
    """
    return get_openai_model(
        model_name="gpt-4o-mini",
        temperature=0.7  # Higher temperature for more natural responses
    )

