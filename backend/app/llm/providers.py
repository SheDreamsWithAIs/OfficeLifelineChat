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
    
    Uses API key authentication via bearer token injection.
    Reads API key from .env file or file path (avoids Windows env var truncation).
    Injects bearer token directly into request headers using boto3 event handlers.
    
    NOTE: There is a known issue with boto3's signing mechanism interfering with
    bearer token authentication. The code implements the correct approach per AWS
    documentation, but boto3 may still attempt AWS credential signing.
    
    See: https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-use.html
    
    Args:
        model_id: Bedrock model ID (default: Claude 3 Haiku for fast/cheap routing)
        temperature: Sampling temperature (0.0-1.0)
        streaming: Enable streaming responses
        
    Returns:
        ChatBedrock: Configured Bedrock model
        
    Raises:
        ValueError: If Bedrock API key is not configured
    """
    import boto3
    from botocore.awsrequest import AWSRequest
    
    # Get API key from settings (reads from .env file or file path)
    settings = get_settings()
    bedrock_key = settings.get_bedrock_key()  # Validates key exists
    
    # Create an Amazon Bedrock client
    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )
    
    # Inject bearer token directly into request headers (avoids Windows env var truncation)
    # This follows AWS documentation pattern but avoids os.environ for long keys
    def inject_bearer_token(request: AWSRequest, **kwargs):
        """Inject bearer token from .env/file into request headers."""
        if request.headers is None:
            request.headers = {}
        request.headers["Authorization"] = f"Bearer {bedrock_key}"
    
    # Register the event handler - this runs before each request is sent
    bedrock_client.meta.events.register('before-send.bedrock-runtime', inject_bearer_token)
    
    # ChatBedrock wraps the boto3 client
    return ChatBedrock(
        model_id=model_id,
        client=bedrock_client,
        region_name="us-east-1",
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
def get_routing_model() -> ChatOpenAI:
    """
    Get model for routing/orchestration (fast and cost-effective).
    
    Uses OpenAI gpt-3.5-turbo for routing (smaller/faster than generation model).
    TODO: Switch to Bedrock Claude 3 Haiku once authentication is resolved.
    
    Returns:
        ChatOpenAI: GPT-3.5-turbo model for routing decisions
    """
    return get_openai_model(
        model_name="gpt-3.5-turbo",
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

