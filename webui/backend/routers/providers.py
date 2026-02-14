"""Provider management router."""

import os
import json
import uuid
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Any
from datetime import datetime

from ..config import get_settings, PROVIDER_CONFIG
from ..schemas.provider import (
    ProviderInfo,
    ProviderConfig,
    ProviderTestRequest,
    ProviderTestResponse,
    CustomProviderInstance,
    CreateCustomProviderRequest,
    UpdateCustomProviderRequest,
    AddModelRequest,
    CopyProviderConfigRequest,
    ProviderWithCustomModels,
)

router = APIRouter()

# Path for storing custom configurations
CONFIG_DIR = Path(__file__).parent.parent.parent / "data"
CONFIG_FILE = CONFIG_DIR / "provider_configs.json"


def _load_configs() -> dict:
    """Load custom provider configurations from file."""
    if not CONFIG_FILE.exists():
        return {"custom_providers": {}, "custom_models": {}}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"custom_providers": {}, "custom_models": {}}


def _save_configs(configs: dict):
    """Save custom provider configurations to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2, ensure_ascii=False, default=str)


def _get_custom_models(provider_id: str) -> list[str]:
    """Get custom models for a provider."""
    configs = _load_configs()
    return configs.get("custom_models", {}).get(provider_id, [])


def _add_custom_model(provider_id: str, model_name: str):
    """Add a custom model to a provider."""
    configs = _load_configs()
    if "custom_models" not in configs:
        configs["custom_models"] = {}
    if provider_id not in configs["custom_models"]:
        configs["custom_models"][provider_id] = []
    if model_name not in configs["custom_models"][provider_id]:
        configs["custom_models"][provider_id].append(model_name)
    _save_configs(configs)


def _remove_custom_model(provider_id: str, model_name: str):
    """Remove a custom model from a provider."""
    configs = _load_configs()
    if provider_id in configs.get("custom_models", {}):
        if model_name in configs["custom_models"][provider_id]:
            configs["custom_models"][provider_id].remove(model_name)
    _save_configs(configs)


@router.get("", response_model=list[ProviderInfo])
async def list_providers() -> list[ProviderInfo]:
    """List all available LLM providers with their configuration status."""
    settings = get_settings()
    providers = []
    configs = _load_configs()

    for provider_id, config in PROVIDER_CONFIG.items():
        env_key = config.get("env_key")
        is_configured = False

        if env_key:
            is_configured = bool(getattr(settings, env_key.lower(), None) or os.environ.get(env_key))
        elif provider_id == "ollama":
            is_configured = True

        # Merge default models with custom models
        default_models = config["models"]
        custom_models = configs.get("custom_models", {}).get(provider_id, [])
        all_models = list(set(default_models + custom_models))

        providers.append(
            ProviderInfo(
                id=provider_id,
                name=config["name"],
                base_url=config.get("base_url"),
                models=all_models,
                is_configured=is_configured,
                supports_custom_models=True,
            )
        )

    # Add custom provider instances
    for instance_id, instance_data in configs.get("custom_providers", {}).items():
        instance = CustomProviderInstance(**instance_data)
        providers.append(
            ProviderInfo(
                id=f"custom:{instance_id}",
                name=instance.name,
                base_url=instance.base_url,
                models=instance.models,
                is_configured=True,  # Custom instances are always configured
                supports_custom_models=True,
            )
        )

    return providers


@router.get("/{provider_id}", response_model=ProviderWithCustomModels)
async def get_provider(provider_id: str) -> ProviderWithCustomModels:
    """Get details of a specific provider with custom models."""
    configs = _load_configs()

    # Check if it's a custom provider instance
    if provider_id.startswith("custom:"):
        instance_id = provider_id[7:]
        if instance_id not in configs.get("custom_providers", {}):
            raise HTTPException(status_code=404, detail="Custom provider not found")
        instance = CustomProviderInstance(**configs["custom_providers"][instance_id])
        return ProviderWithCustomModels(
            id=provider_id,
            name=instance.name,
            base_url=instance.base_url,
            default_models=[],
            custom_models=instance.models,
            all_models=instance.models,
            is_configured=True,
            supports_custom_models=True,
        )

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

    default_models = config["models"]
    custom_models = configs.get("custom_models", {}).get(provider_id, [])
    all_models = list(set(default_models + custom_models))

    return ProviderWithCustomModels(
        id=provider_id,
        name=config["name"],
        base_url=config.get("base_url"),
        default_models=default_models,
        custom_models=custom_models,
        all_models=all_models,
        is_configured=is_configured,
        supports_custom_models=True,
    )


@router.post("/configure")
async def configure_provider(config: ProviderConfig) -> dict[str, Any]:
    """Configure an LLM provider with API key."""
    if config.provider_id.startswith("custom:"):
        raise HTTPException(status_code=400, detail="Use /custom/{instance_id} to update custom providers")

    if config.provider_id not in PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail=f"Provider '{config.provider_id}' not found")

    provider_config = PROVIDER_CONFIG[config.provider_id]
    env_key = provider_config.get("env_key")

    if env_key:
        os.environ[env_key] = config.api_key
        if config.provider_id == "newapi" and config.base_url:
            os.environ["NEWAPI_BASE_URL"] = config.base_url

    # Save custom models if provided
    if config.models:
        configs = _load_configs()
        if "custom_models" not in configs:
            configs["custom_models"] = {}
        configs["custom_models"][config.provider_id] = config.models
        _save_configs(configs)

    return {
        "success": True,
        "message": f"Provider '{config.provider_id}' configured successfully",
    }


# ============ Custom Provider Instance Management ============

@router.post("/custom", response_model=CustomProviderInstance)
async def create_custom_provider(request: CreateCustomProviderRequest) -> CustomProviderInstance:
    """Create a new custom provider instance (e.g., multiple NewAPI endpoints)."""
    instance_id = str(uuid.uuid4())[:8]
    now = datetime.now()

    instance = CustomProviderInstance(
        instance_id=instance_id,
        name=request.name,
        provider_type=request.provider_type,
        base_url=request.base_url,
        api_key=request.api_key,
        models=request.models,
        created_at=now,
        updated_at=now,
    )

    configs = _load_configs()
    if "custom_providers" not in configs:
        configs["custom_providers"] = {}
    configs["custom_providers"][instance_id] = instance.model_dump()
    _save_configs(configs)

    return instance


@router.get("/custom/list", response_model=list[CustomProviderInstance])
async def list_custom_providers() -> list[CustomProviderInstance]:
    """List all custom provider instances."""
    configs = _load_configs()
    instances = []
    for instance_data in configs.get("custom_providers", {}).values():
        instances.append(CustomProviderInstance(**instance_data))
    return instances


@router.get("/custom/{instance_id}", response_model=CustomProviderInstance)
async def get_custom_provider(instance_id: str) -> CustomProviderInstance:
    """Get a specific custom provider instance."""
    configs = _load_configs()
    if instance_id not in configs.get("custom_providers", {}):
        raise HTTPException(status_code=404, detail="Custom provider not found")
    return CustomProviderInstance(**configs["custom_providers"][instance_id])


@router.put("/custom/{instance_id}", response_model=CustomProviderInstance)
async def update_custom_provider(
    instance_id: str,
    request: UpdateCustomProviderRequest,
) -> CustomProviderInstance:
    """Update a custom provider instance."""
    configs = _load_configs()
    if instance_id not in configs.get("custom_providers", {}):
        raise HTTPException(status_code=404, detail="Custom provider not found")

    instance_data = configs["custom_providers"][instance_id]

    if request.name is not None:
        instance_data["name"] = request.name
    if request.base_url is not None:
        instance_data["base_url"] = request.base_url
    if request.api_key is not None:
        instance_data["api_key"] = request.api_key
    if request.models is not None:
        instance_data["models"] = request.models

    instance_data["updated_at"] = datetime.now().isoformat()
    configs["custom_providers"][instance_id] = instance_data
    _save_configs(configs)

    return CustomProviderInstance(**instance_data)


@router.delete("/custom/{instance_id}")
async def delete_custom_provider(instance_id: str) -> dict[str, str]:
    """Delete a custom provider instance."""
    configs = _load_configs()
    if instance_id not in configs.get("custom_providers", {}):
        raise HTTPException(status_code=404, detail="Custom provider not found")

    del configs["custom_providers"][instance_id]
    _save_configs(configs)

    return {"message": f"Custom provider '{instance_id}' deleted"}


@router.post("/custom/{instance_id}/copy", response_model=CustomProviderInstance)
async def copy_custom_provider(
    instance_id: str,
    request: CopyProviderConfigRequest,
) -> CustomProviderInstance:
    """Copy a custom provider configuration to a new instance."""
    configs = _load_configs()

    # Check if source exists
    if instance_id not in configs.get("custom_providers", {}):
        raise HTTPException(status_code=404, detail="Source custom provider not found")

    source = configs["custom_providers"][instance_id]

    # Create new instance
    new_instance_id = str(uuid.uuid4())[:8]
    now = datetime.now()

    new_instance = CustomProviderInstance(
        instance_id=new_instance_id,
        name=request.new_name,
        provider_type=source["provider_type"],
        base_url=source["base_url"],
        api_key=source["api_key"],
        models=source["models"].copy(),
        created_at=now,
        updated_at=now,
    )

    configs["custom_providers"][new_instance_id] = new_instance.model_dump()
    _save_configs(configs)

    return new_instance


# ============ Model Management ============

@router.post("/{provider_id}/models")
async def add_model(provider_id: str, request: AddModelRequest) -> dict[str, Any]:
    """Add a custom model to a provider."""
    if provider_id.startswith("custom:"):
        # For custom providers, update the instance directly
        instance_id = provider_id[7:]
        configs = _load_configs()
        if instance_id not in configs.get("custom_providers", {}):
            raise HTTPException(status_code=404, detail="Custom provider not found")

        instance_data = configs["custom_providers"][instance_id]
        if request.model_name not in instance_data["models"]:
            instance_data["models"].append(request.model_name)
            instance_data["updated_at"] = datetime.now().isoformat()
            configs["custom_providers"][instance_id] = instance_data
            _save_configs(configs)

        return {"success": True, "message": f"Model '{request.model_name}' added"}

    # For built-in providers, add to custom models
    if provider_id not in PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")

    _add_custom_model(provider_id, request.model_name)
    return {"success": True, "message": f"Model '{request.model_name}' added to {provider_id}"}


@router.delete("/{provider_id}/models/{model_name}")
async def remove_model(provider_id: str, model_name: str) -> dict[str, Any]:
    """Remove a custom model from a provider."""
    if provider_id.startswith("custom:"):
        instance_id = provider_id[7:]
        configs = _load_configs()
        if instance_id not in configs.get("custom_providers", {}):
            raise HTTPException(status_code=404, detail="Custom provider not found")

        instance_data = configs["custom_providers"][instance_id]
        if model_name in instance_data["models"]:
            instance_data["models"].remove(model_name)
            instance_data["updated_at"] = datetime.now().isoformat()
            configs["custom_providers"][instance_id] = instance_data
            _save_configs(configs)

        return {"success": True, "message": f"Model '{model_name}' removed"}

    _remove_custom_model(provider_id, model_name)
    return {"success": True, "message": f"Model '{model_name}' removed from {provider_id}"}


# ============ Connection Testing ============

@router.post("/test", response_model=ProviderTestResponse)
async def test_provider(request: ProviderTestRequest) -> ProviderTestResponse:
    """Test connection to an LLM provider."""
    configs = _load_configs()

    try:
        from tradingagents.llm_clients.factory import create_llm_client

        base_url = None
        provider_type = request.provider_id
        api_key = None

        # Handle custom provider instances
        if request.provider_id.startswith("custom:"):
            instance_id = request.provider_id[7:]
            if instance_id not in configs.get("custom_providers", {}):
                return ProviderTestResponse(
                    success=False,
                    message="Custom provider not found",
                )
            instance = configs["custom_providers"][instance_id]
            base_url = instance["base_url"]
            provider_type = instance["provider_type"]
            api_key = instance["api_key"]

        elif request.provider_id == "newapi":
            base_url = os.environ.get("NEWAPI_BASE_URL")
            if not base_url:
                return ProviderTestResponse(
                    success=False,
                    message="NewAPI requires base_url to be configured",
                )

        start_time = time.time()

        # Build kwargs for client creation
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key

        client = create_llm_client(
            provider=provider_type,
            model=request.model,
            base_url=base_url,
            **client_kwargs,
        )

        llm = client.get_llm()

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
