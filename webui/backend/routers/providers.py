"""Provider management router."""

import os
import time
from fastapi import APIRouter, HTTPException
from typing import Any

from ..config import get_settings, PROVIDER_CONFIG
from ..schemas.provider import (
    ProviderInfo,
    ProviderConfig,
    ProviderTestRequest,
    ProviderTestResponse,
)

router = APIRouter()


@router.get("", response_model=list[ProviderInfo])
async def list_providers() -> list[ProviderInfo]:
    """List all available LLM providers with their configuration status."""
    settings = get_settings()
    providers = []

    for provider_id, config in PROVIDER_CONFIG.items():
        env_key = config.get("env_key")
        is_configured = False

        if env_key:
            is_configured = bool(getattr(settings, env_key.lower(), None) or os.environ.get(env_key))
        elif provider_id == "ollama":
            is_configured = True  # Ollama doesn't require API key

        providers.append(
            ProviderInfo(
                id=provider_id,
                name=config["name"],
                base_url=config.get("base_url"),
                models=config["models"],
                is_configured=is_configured,
            )
        )

    return providers


@router.get("/{provider_id}", response_model=ProviderInfo)
async def get_provider(provider_id: str) -> ProviderInfo:
    """Get details of a specific provider."""
    if provider_id not in PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")

    settings = get_settings()
    config = PROVIDER_CONFIG[provider_id]
    env_key = config.get("env_key")
    is_configured = False

    if env_key:
        is_configured = bool(getattr(settings, env_key.lower(), None) or os.environ.get(env_key))
    elif provider_id == "ollama":
        is_configured = True

    return ProviderInfo(
        id=provider_id,
        name=config["name"],
        base_url=config.get("base_url"),
        models=config["models"],
        is_configured=is_configured,
    )


@router.post("/configure")
async def configure_provider(config: ProviderConfig) -> dict[str, Any]:
    """Configure an LLM provider with API key.

    Note: This sets the API key in memory for the current session.
    For persistent configuration, set the environment variable.
    """
    if config.provider_id not in PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail=f"Provider '{config.provider_id}' not found")

    provider_config = PROVIDER_CONFIG[config.provider_id]
    env_key = provider_config.get("env_key")

    if env_key:
        # Set in environment for this session
        os.environ[env_key] = config.api_key

        # For newapi, also set base_url if provided
        if config.provider_id == "newapi" and config.base_url:
            os.environ["NEWAPI_BASE_URL"] = config.base_url

    return {
        "success": True,
        "message": f"Provider '{config.provider_id}' configured successfully",
    }


@router.post("/test", response_model=ProviderTestResponse)
async def test_provider(request: ProviderTestRequest) -> ProviderTestResponse:
    """Test connection to an LLM provider."""
    if request.provider_id not in PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail=f"Provider '{request.provider_id}' not found")

    try:
        from tradingagents.llm_clients.factory import create_llm_client

        # Get base_url for newapi
        base_url = None
        if request.provider_id == "newapi":
            base_url = os.environ.get("NEWAPI_BASE_URL")
            if not base_url:
                return ProviderTestResponse(
                    success=False,
                    message="NewAPI requires base_url to be configured",
                )

        start_time = time.time()

        # Create client
        client = create_llm_client(
            provider=request.provider_id,
            model=request.model,
            base_url=base_url,
        )

        # Get LLM instance
        llm = client.get_llm()

        # Simple test call
        try:
            response = llm.invoke("Say 'OK' if you can read this.")
            latency_ms = (time.time() - start_time) * 1000

            return ProviderTestResponse(
                success=True,
                message=f"Successfully connected to {request.provider_id}",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as e:
            return ProviderTestResponse(
                success=False,
                message=f"Connection test failed: {str(e)}",
            )

    except Exception as e:
        return ProviderTestResponse(
            success=False,
            message=f"Failed to create client: {str(e)}",
        )
