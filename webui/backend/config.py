"""Configuration management for WebUI backend."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server settings
    app_name: str = "TradingAgents WebUI"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # LLM Provider API Keys
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    zhipu_api_key: Optional[str] = None
    minimax_api_key: Optional[str] = None
    newapi_api_key: Optional[str] = None
    newapi_base_url: Optional[str] = None

    # Data provider settings
    finnhub_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Provider configurations
PROVIDER_CONFIG = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "models": [
            "gpt-5.2", "gpt-5.1", "gpt-5", "gpt-5-mini", "gpt-5-nano",
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
            "o4-mini", "o3", "o3-mini", "o1", "o1-preview",
            "gpt-4o", "gpt-4o-mini",
        ],
    },
    "anthropic": {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/",
        "env_key": "ANTHROPIC_API_KEY",
        "models": [
            "claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5",
            "claude-opus-4-1-20250805", "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022",
        ],
    },
    "google": {
        "name": "Google",
        "base_url": "https://generativelanguage.googleapis.com/v1",
        "env_key": "GOOGLE_API_KEY",
        "models": [
            "gemini-3-pro-preview", "gemini-3-flash-preview",
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
            "gemini-2.0-flash", "gemini-2.0-flash-lite",
        ],
    },
    "xai": {
        "name": "xAI",
        "base_url": "https://api.x.ai/v1",
        "env_key": "XAI_API_KEY",
        "models": [
            "grok-4-1-fast", "grok-4-1-fast-reasoning", "grok-4-1-fast-non-reasoning",
            "grok-4", "grok-4-0709", "grok-4-fast-reasoning", "grok-4-fast-non-reasoning",
        ],
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "models": ["nvidia/nemotron-3-nano-30b-a3b:free", "z-ai/glm-4.5-air:free"],
    },
    "ollama": {
        "name": "Ollama",
        "base_url": "http://localhost:11434/v1",
        "env_key": None,
        "models": ["qwen3:latest", "gpt-oss:latest", "glm-4.7-flash:latest"],
    },
    "zhipu": {
        "name": "Zhipu AI (智谱)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "env_key": "ZHIPU_API_KEY",
        "models": [
            "glm-4-plus", "glm-4-0520", "glm-4", "glm-4-air", "glm-4-airx",
            "glm-4-long", "glm-4-flash", "glm-4-flashx",
            "glm-4v", "glm-4v-plus", "glm-4v-flash",
        ],
    },
    "minimax": {
        "name": "MiniMax",
        "base_url": "https://api.minimax.chat/v1",
        "env_key": "MINIMAX_API_KEY",
        "models": [
            "abab6.5s-chat", "abab6.5g-chat", "abab6.5t-chat",
            "abab5.5-chat", "abab5.5s-chat", "abab5.5t-chat",
            "minimax-01", "minimax-text-01",
        ],
    },
    "newapi": {
        "name": "NewAPI (自定义)",
        "base_url": None,
        "env_key": "NEWAPI_API_KEY",
        "models": [],  # Custom models, user-defined
    },
}

# Market configurations
MARKET_CONFIG = {
    "us": {
        "name": "美股",
        "data_source": "yfinance",
        "symbol_format": "AAPL",
        "description": "US stock market",
    },
    "hk": {
        "name": "港股",
        "data_source": "yfinance",
        "symbol_format": "0700.HK",
        "description": "Hong Kong stock market",
    },
    "cn": {
        "name": "A股",
        "data_source": "akshare",
        "symbol_format": "000001.SZ",
        "description": "Chinese A-share market",
    },
}
