from typing import Optional

from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .google_client import GoogleClient


def create_llm_client(
    provider: str,
    model: str,
    base_url: Optional[str] = None,
    **kwargs,
) -> BaseLLMClient:
    """Create an LLM client for the specified provider.

    Args:
        provider: LLM provider (openai, anthropic, google, xai, ollama, openrouter,
                  zhipu, minimax, newapi)
        model: Model name/identifier
        base_url: Optional base URL for API endpoint
        **kwargs: Additional provider-specific arguments

    Returns:
        Configured BaseLLMClient instance

    Raises:
        ValueError: If provider is not supported
    """
    provider_lower = provider.lower()

    if provider_lower in ("openai", "ollama", "openrouter"):
        return OpenAIClient(model, base_url, provider=provider_lower, **kwargs)

    if provider_lower == "xai":
        return OpenAIClient(model, base_url, provider="xai", **kwargs)

    # Zhipu AI (智谱) - OpenAI-compatible API
    if provider_lower == "zhipu":
        return OpenAIClient(
            model,
            base_url or "https://open.bigmodel.cn/api/paas/v4/",
            provider="zhipu",
            **kwargs,
        )

    # MiniMax - OpenAI-compatible API
    if provider_lower == "minimax":
        return OpenAIClient(
            model,
            base_url or "https://api.minimax.chat/v1",
            provider="minimax",
            **kwargs,
        )

    # NewAPI - Custom OpenAI-compatible API (requires base_url)
    if provider_lower == "newapi":
        if not base_url:
            raise ValueError("newapi provider requires base_url to be configured")
        return OpenAIClient(model, base_url, provider="newapi", **kwargs)

    if provider_lower == "anthropic":
        return AnthropicClient(model, base_url, **kwargs)

    if provider_lower == "google":
        return GoogleClient(model, base_url, **kwargs)

    # Handle any unknown provider as OpenAI-compatible (for custom providers)
    # This allows custom OpenAI-compatible APIs to work
    if base_url:
        return OpenAIClient(model, base_url, provider=provider_lower, **kwargs)

    raise ValueError(f"Unsupported LLM provider: {provider}. For custom providers, provide a base_url.")
