"""Provider-related schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ProviderInfo(BaseModel):
    """Information about an LLM provider."""

    id: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Display name")
    base_url: Optional[str] = Field(None, description="API base URL")
    models: list[str] = Field(default_factory=list, description="Available models")
    is_configured: bool = Field(False, description="Whether API key is configured")


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider_id: str = Field(..., description="Provider identifier")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL (for newapi)")


class ProviderTestRequest(BaseModel):
    """Request to test provider connection."""

    provider_id: str = Field(..., description="Provider identifier")
    model: str = Field(..., description="Model to test with")


class ProviderTestResponse(BaseModel):
    """Response from provider connection test."""

    success: bool = Field(..., description="Whether the test was successful")
    message: str = Field(..., description="Status message")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")
