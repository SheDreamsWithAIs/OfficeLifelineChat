"""
Backend configuration management.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


def find_env_file() -> str:
    """
    Find .env file in project root (parent of backend/).
    
    Returns:
        Path to .env file
    """
    # Get backend directory (where this file is)
    backend_dir = Path(__file__).parent.parent.parent
    # Go up to project root
    project_root = backend_dir.parent
    env_path = project_root / ".env"
    return str(env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=find_env_file(),  # Look for .env in project root
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # AWS Bedrock Configuration (API key authentication)
    aws_bedrock_api_key: Optional[str] = Field(
        default=None,
        description="AWS Bedrock API key (optional, required for orchestrator)"
    )
    
    # ChromaDB Configuration
    chroma_db_path: str = Field(
        default="./chroma_db",
        description="Path to ChromaDB persistence directory"
    )
    
    # Server Configuration
    backend_port: int = Field(
        default=8000,
        description="Backend server port"
    )
    
    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("OPENAI_API_KEY cannot be empty")
        if "your_openai_api_key_here" in v.lower():
            raise ValueError("Please set a valid OPENAI_API_KEY in .env file")
        return v.strip()
    
    @field_validator("aws_bedrock_api_key")
    @classmethod
    def validate_bedrock_key(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate AWS Bedrock API key if provided.
        
        Includes checks for common truncation issues.
        """
        if v is None:
            return None
        v = v.strip()
        if v == "":
            return None
        if "your_aws_bedrock_api_key_here" in v.lower():
            raise ValueError("Please set a valid AWS_BEDROCK_API_KEY in .env file")
        
        # Warn if key seems too short (common truncation issue)
        if len(v) < 20:
            raise ValueError(
                f"AWS_BEDROCK_API_KEY appears truncated (length: {len(v)}). "
                "Bedrock API keys are typically much longer. Check for line breaks or missing characters."
            )
        
        return v
    
    def get_bedrock_key(self) -> str:
        """
        Get Bedrock API key, raising error if not set.
        
        Returns:
            Bedrock API key string
            
        Raises:
            ValueError: If Bedrock key is not configured
        """
        if not self.aws_bedrock_api_key:
            raise ValueError(
                "AWS_BEDROCK_API_KEY is required for Bedrock operations. "
                "Please set it in .env file."
            )
        return self.aws_bedrock_api_key
    
    @field_validator("chroma_db_path")
    @classmethod
    def validate_chroma_path(cls, v: str) -> str:
        """Ensure ChromaDB path is valid."""
        # Normalize path separators
        normalized = os.path.normpath(v)
        return normalized


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.
    
    Returns:
        Settings: The application settings
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            raise RuntimeError(
                f"Failed to load settings: {e}\n"
                "Please ensure .env file exists with required variables."
            ) from e
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)."""
    global _settings
    _settings = None
    return get_settings()

