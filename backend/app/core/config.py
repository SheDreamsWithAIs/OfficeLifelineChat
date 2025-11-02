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
    # Note: Bedrock uses AWS_BEARER_TOKEN_BEDROCK environment variable
    # We accept either AWS_BEDROCK_API_KEY or AWS_BEARER_TOKEN_BEDROCK from .env
    aws_bedrock_api_key: Optional[str] = Field(
        default=None,
        description="AWS Bedrock API key (optional, required for orchestrator). Maps to AWS_BEARER_TOKEN_BEDROCK"
    )
    
    # Also check for AWS_BEARER_TOKEN_BEDROCK directly
    aws_bearer_token_bedrock: Optional[str] = Field(
        default=None,
        alias="AWS_BEARER_TOKEN_BEDROCK",
        description="AWS Bedrock Bearer Token (alternative name)"
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
        Note: This value should be set as AWS_BEARER_TOKEN_BEDROCK in .env
        """
        if v is None:
            return None
        v = v.strip()
        if v == "":
            return None
        if "your_aws_bedrock_api_key_here" in v.lower():
            raise ValueError("Please set a valid AWS_BEDROCK_API_KEY (maps to AWS_BEARER_TOKEN_BEDROCK) in .env file")
        
        # Warn if key seems too short (common truncation issue)
        # Bedrock API keys are typically very long (1000+ characters)
        if len(v) < 100:
            raise ValueError(
                f"AWS_BEDROCK_API_KEY appears truncated (length: {len(v)}). "
                "Bedrock API keys are typically 1000+ characters. Check for line breaks or missing characters."
            )
        
        return v
    
    def get_bedrock_key(self) -> str:
        """
        Get Bedrock API key, checking multiple sources in order:
        1. Windows OS environment variable BEDROCK_API_KEY_PATH (points to file) - PREFERRED
        2. Direct value from AWS_BEDROCK_API_KEY or AWS_BEARER_TOKEN_BEDROCK in .env
        3. Path to file from BEDROCK_API_KEY_PATH in .env file
        
        Method 1 is preferred because Windows env vars can store short paths without truncation,
        then we read the long key from the file.
        
        Returns:
            Bedrock API key string
            
        Raises:
            ValueError: If Bedrock key is not configured or file cannot be read
        """
        key = None
        
        # Method 1: Check Windows OS environment variable for file path (short, won't truncate)
        api_key_path = os.environ.get("BEDROCK_API_KEY_PATH")
        if api_key_path:
            api_key_path = os.path.normpath(api_key_path)
            if not os.path.isabs(api_key_path):
                # Relative path - resolve from project root
                project_root = Path(__file__).parent.parent.parent.parent
                api_key_path = project_root / api_key_path
            
            if os.path.exists(api_key_path):
                try:
                    with open(api_key_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        # If file has multiple lines, take first non-empty line
                        # This handles cases where file might have comments or other content
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        if lines:
                            key = lines[0]  # Take first non-empty line
                        else:
                            raise ValueError(f"File {api_key_path} appears to be empty")
                except Exception as e:
                    raise ValueError(
                        f"Failed to read Bedrock API key from file {api_key_path}: {e}"
                    )
        
        # Method 2: Check for direct key in .env (may truncate if >1000 chars on Windows)
        if not key:
            key = self.aws_bearer_token_bedrock or self.aws_bedrock_api_key
        
        if not key:
            raise ValueError(
                "AWS Bedrock API key is required. "
                "Please set one of:\n"
                "  1. Windows OS env var: BEDROCK_API_KEY_PATH=<path_to_key_file> (PREFERRED)\n"
                "  2. .env file: AWS_BEDROCK_API_KEY or AWS_BEARER_TOKEN_BEDROCK\n"
                "  3. .env file: BEDROCK_API_KEY_PATH=<path_to_key_file>"
            )
        return key
    
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

