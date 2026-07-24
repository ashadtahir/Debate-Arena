"""Abstract LLM client with provider-swappable implementations."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from ai.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class CompletionResult:
    content: str
    usage: TokenUsage = field(default_factory=TokenUsage)


class LLMClient(ABC):
    """Protocol for LLM providers. Swap implementations without touching the debate engine."""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        response_format: dict | None = None,
    ) -> CompletionResult:
        ...


class OpenAICompatibleClient(LLMClient):
    """Works with OpenAI, OpenRouter, Groq, Together, and any OpenAI-compatible API."""

    def __init__(self) -> None:
        s = get_settings()
        self.api_key = s.api_key
        self.base_url = s.base_url.rstrip("/")
        self.model = s.model

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        response_format: dict | None = None,
    ) -> CompletionResult:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            usage_data = data.get("usage") or {}
            usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

            return CompletionResult(content=content, usage=usage)


class StubClient(LLMClient):
    """Returns a mock response for development without an API key."""

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        response_format: dict | None = None,
    ) -> CompletionResult:
        user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        return CompletionResult(
            content=json.dumps({
                "response": f"That is a thought-provoking claim. But let me ask you: what evidence supports your position? You stated '{user_msg[:80]}...' \u2014 can you defend that under scrutiny?",
                "thinking_style": "analytical questioning",
                "next_focus": "demand evidence for the core claim",
                "tone": "measured but challenging",
            }),
            usage=TokenUsage(),
        )


def get_llm_client() -> LLMClient:
    """Factory: returns the configured LLM client based on environment."""
    s = get_settings()
    provider = s.provider.lower()

    if provider in ("openai", "openrouter", "groq", "together", "deepseek"):
        return OpenAICompatibleClient()
    elif provider == "stub":
        return StubClient()
    else:
        logger.warning("Unknown provider '%s', defaulting to OpenAI-compatible client", provider)
        return OpenAICompatibleClient()
