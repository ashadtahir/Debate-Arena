"""Debate engine: orchestrates prompt construction, LLM calls, and response parsing."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from ai.config import get_settings
from ai.enums import DebateSide, Difficulty, Persona
from ai.llm_client import LLMClient, get_llm_client
from ai.models import ConversationTurn
from ai.persona_manager import get_persona_config
from ai.prompt_builder import build_messages
from ai.response_parser import parse_llm_response

logger = logging.getLogger(__name__)


@dataclass
class DebateRequest:
    persona_id: Persona
    topic: str
    side: DebateSide
    difficulty: Difficulty
    round_number: int
    history: list[ConversationTurn] = field(default_factory=list)
    user_argument: str = ""


@dataclass
class DebateResponse:
    response: str
    thinking_style: str
    next_focus: str
    tone: str
    persona_id: Persona
    round_number: int
    parse_success: bool


class DebateEngine:
    """Stateless debate engine. Accepts an LLM client via constructor (dependency injection)."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or get_llm_client()

    async def generate_response(self, request: DebateRequest) -> DebateResponse:
        persona = get_persona_config(request.persona_id)
        s = get_settings()

        messages = build_messages(
            persona=persona,
            topic=request.topic,
            side=request.side,
            difficulty=request.difficulty,
            round_number=request.round_number,
            history=request.history,
            user_argument=request.user_argument,
        )

        system_content = messages[0]["content"]
        prompt_len = len(system_content)

        start = time.monotonic()
        try:
            result = await self._llm.complete(
                messages,
                temperature=s.temperature,
                max_tokens=s.max_tokens,
                response_format={"type": "json_object"},
            )
            elapsed_ms = round((time.monotonic() - start) * 1000)
            parsed = parse_llm_response(result.content)

            logger.info(
                "provider=%s model=%s persona=%s difficulty=%s round=%d "
                "prompt_version=%s prompt_len=%d response_ms=%d "
                "parse_ok=%s prompt_tokens=%d completion_tokens=%d total_tokens=%d",
                s.provider,
                s.model,
                request.persona_id.value,
                request.difficulty.value,
                request.round_number,
                persona.prompt_version,
                prompt_len,
                elapsed_ms,
                parsed.parse_success,
                result.usage.prompt_tokens,
                result.usage.completion_tokens,
                result.usage.total_tokens,
            )

            return DebateResponse(
                response=parsed.response,
                thinking_style=parsed.thinking_style,
                next_focus=parsed.next_focus,
                tone=parsed.tone,
                persona_id=request.persona_id,
                round_number=request.round_number,
                parse_success=parsed.parse_success,
            )

        except Exception:
            elapsed_ms = round((time.monotonic() - start) * 1000)
            logger.exception(
                "provider=%s model=%s persona=%s difficulty=%s round=%d "
                "prompt_version=%s prompt_len=%d response_ms=%d",
                s.provider,
                s.model,
                request.persona_id.value,
                request.difficulty.value,
                request.round_number,
                persona.prompt_version,
                prompt_len,
                elapsed_ms,
            )
            raise
