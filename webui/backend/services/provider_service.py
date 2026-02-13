"""Provider management service."""

import os
from typing import Optional
from ..config import get_settings, PROVIDER_CONFIG


class ProviderService:
    """Service for managing LLM providers."""

    @staticmethod
    def get_provider_config(provider_id: str) -> Optional[dict]:
        """Get configuration for a provider."""
        return PROVIDER_CONFIG.get(provider_id)

    @staticmethod
    def is_provider_configured(provider_id: str) -> bool:
        """Check if a provider has API key configured."""
        config = PROVIDER_CONFIG.get(provider_id)
        if not config:
            return False

        env_key = config.get("env_key")
        if not env_key:
            # Ollama doesn't require API key
            return provider_id == "ollama"

        settings = get_settings()
        return bool(
            getattr(settings, env_key.lower(), None)
            or os.environ.get(env_key)
        )

    @staticmethod
    def set_provider_api_key(provider_id: str, api_key: str, base_url: Optional[str] = None):
        """Set API key for a provider."""
        config = PROVIDER_CONFIG.get(provider_id)
        if not config:
            raise ValueError(f"Unknown provider: {provider_id}")

        env_key = config.get("env_key")
        if env_key:
            os.environ[env_key] = api_key

        # Handle custom base_url for newapi
        if provider_id == "newapi" and base_url:
            os.environ["NEWAPI_BASE_URL"] = base_url

    @staticmethod
    def get_all_providers() -> list[dict]:
        """Get all providers with their status."""
        providers = []
        for provider_id, config in PROVIDER_CONFIG.items():
            providers.append({
                "id": provider_id,
                "name": config["name"],
                "base_url": config.get("base_url"),
                "models": config["models"],
                "is_configured": ProviderService.is_provider_configured(provider_id),
            })
        return providers
