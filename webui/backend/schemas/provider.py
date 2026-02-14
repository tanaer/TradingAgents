"""Provider-related schemas."""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ProviderInfo(BaseModel):
    """Information about an LLM provider."""

    id: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Display name")
    base_url: Optional[str] = Field(None, description="API base URL")
    models: list[str] = Field(default_factory=list, description="Available models")
    is_configured: bool = Field(False, description="Whether API key is configured")
    supports_custom_models: bool = Field(True, description="Whether custom models can be added")


class CustomProviderInstance(BaseModel):
    """A custom provider instance (for NewAPI or custom configurations)."""

    instance_id: str = Field(..., description="Unique instance identifier")
    name: str = Field(..., description="Display name for this instance")
    provider_type: str = Field(..., description="Base provider type (e.g., 'newapi', 'openai')")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    models: list[str] = Field(default_factory=list, description="Available models for this instance")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider_id: str = Field(..., description="Provider identifier")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL (for newapi)")
    models: Optional[list[str]] = Field(None, description="Custom models list (optional)")


class CreateCustomProviderRequest(BaseModel):
    """Request to create a custom provider instance."""

    name: str = Field(..., description="Display name for this instance")
    provider_type: str = Field(default="newapi", description="Provider type")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    models: list[str] = Field(default_factory=list, description="Initial models")


class UpdateCustomProviderRequest(BaseModel):
    """Request to update a custom provider instance."""

    name: Optional[str] = Field(None, description="Display name")
    base_url: Optional[str] = Field(None, description="API base URL")
    api_key: Optional[str] = Field(None, description="API key")
    models: Optional[list[str]] = Field(None, description="Models list")


class AddModelRequest(BaseModel):
    """Request to add a model to a provider."""

    model_name: str = Field(..., description="Model name to add")


class ProviderTestRequest(BaseModel):
    """Request to test provider connection."""

    provider_id: str = Field(..., description="Provider identifier")
    model: str = Field(..., description="Model to test with")
    instance_id: Optional[str] = Field(None, description="Custom instance ID (for custom providers)")


class ProviderTestResponse(BaseModel):
    """Response from provider connection test."""

    success: bool = Field(..., description="Whether the test was successful")
    message: str = Field(..., description="Status message")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")


class CopyProviderConfigRequest(BaseModel):
    """Request to copy a provider configuration."""

    source_instance_id: str = Field(..., description="Source instance to copy from")
    new_name: str = Field(..., description="Name for the new instance")


class ProviderWithCustomModels(BaseModel):
    """Provider info with custom models merged."""

    id: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Display name")
    base_url: Optional[str] = Field(None, description="API base URL")
    default_models: list[str] = Field(default_factory=list, description="Default models")
    custom_models: list[str] = Field(default_factory=list, description="Custom added models")
    all_models: list[str] = Field(default_factory=list, description="All models (default + custom)")
    is_configured: bool = Field(False, description="Whether API key is configured")
    supports_custom_models: bool = Field(True, description="Whether custom models can be added")
