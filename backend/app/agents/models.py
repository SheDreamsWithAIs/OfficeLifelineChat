"""
Pydantic models for structured agent responses.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/models
"""

from typing import Optional
from pydantic import BaseModel, Field


class PolicyResponse(BaseModel):
    """Structured response format for Policy Agent."""
    
    friendly_response: str = Field(
        description="A friendly, conversational introduction or summary (1-2 sentences)"
    )
    policy_description: str = Field(
        description="Detailed description of the policy information, including all key sections and details"
    )
    key_points: Optional[list[str]] = Field(
        default=None,
        description="List of key points or sections if applicable"
    )
    contact_info: Optional[str] = Field(
        default=None,
        description="Contact information if relevant to the query"
    )


class TechnicalResponse(BaseModel):
    """Structured response format for Technical Agent."""
    
    friendly_response: str = Field(
        description="A friendly, conversational introduction (1-2 sentences)"
    )
    technical_description: str = Field(
        description="Detailed technical information, troubleshooting steps, solutions, and explanations"
    )
    steps: Optional[list[str]] = Field(
        default=None,
        description="Step-by-step instructions if applicable"
    )
    code_examples: Optional[list[str]] = Field(
        default=None,
        description="Code examples or snippets if applicable"
    )
    error_codes: Optional[list[str]] = Field(
        default=None,
        description="Specific error codes and their solutions if applicable"
    )


class BillingResponse(BaseModel):
    """Structured response format for Billing Agent."""
    
    friendly_response: str = Field(
        description="A friendly, conversational introduction (1-2 sentences)"
    )
    billing_description: str = Field(
        description="Detailed billing information, pricing, plans, and payment details"
    )
    plans: Optional[list[dict]] = Field(
        default=None,
        description="Pricing plans with details if applicable"
    )
    payment_info: Optional[str] = Field(
        default=None,
        description="Payment methods and billing cycle information if applicable"
    )

