"""
Pydantic models for FastAPI request/response schemas.

LangChain Version: v1.0+
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""
    
    message: str = Field(..., description="User message to send to the agent")
    thread_id: Optional[str] = Field(
        default=None,
        description="Conversation thread ID for maintaining context. If not provided, a new conversation starts."
    )
    stream: bool = Field(
        default=True,
        description="Whether to stream the response (default: True)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is your privacy policy?",
                "thread_id": "user_123",
                "stream": True
            }
        }


class ChatResponse(BaseModel):
    """Response model for non-streaming /chat endpoint."""
    
    response: str = Field(..., description="Agent's response message")
    thread_id: str = Field(..., description="Conversation thread ID")
    agent_type: Optional[str] = Field(
        default=None,
        description="Type of agent that handled the query (policy, technical, billing)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Our privacy policy outlines how we collect and use your data...",
                "thread_id": "user_123",
                "agent_type": "policy"
            }
        }


class ChatStreamChunk(BaseModel):
    """Model for streaming response chunks."""
    
    content: str = Field(..., description="Chunk of response content")
    done: bool = Field(default=False, description="Whether this is the final chunk")
    thread_id: Optional[str] = Field(
        default=None,
        description="Conversation thread ID"
    )
    agent_type: Optional[str] = Field(
        default=None,
        description="Type of agent handling the query"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Our privacy policy",
                "done": False,
                "thread_id": "user_123",
                "agent_type": "policy"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(
        default=None,
        description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Internal server error",
                "detail": "Agent execution failed"
            }
        }

