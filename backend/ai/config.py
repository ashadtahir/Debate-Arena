"""Centralized configuration via pydantic-settings. All env vars in one place.

All settings are prefixed with LLM_ (e.g., LLM_PROVIDER, LLM_API_KEY).
The Settings class is a singleton via lru_cache — call get_settings() anywhere.

Supported providers: stub, openai, openrouter, groq, together, deepseek.
All use the OpenAI-compatible chat completions API format.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "LLM_", "env_file": ".env", "extra": "ignore"}

    provider: str = "stub"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024

    # App
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
