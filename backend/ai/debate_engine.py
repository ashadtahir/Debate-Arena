"""Debate engine — orchestrates prompt construction, LLM calls, and response parsing.

This is the core AI module. It takes a DebateRequest (persona, topic, side,
difficulty, round, history, user argument), builds a prompt via prompt_builder,
calls the LLM, and parses the JSON response into a DebateResponse.

The engine is stateless and accepts an LLMClient via constructor (dependency
injection), making it easy to swap providers or inject test doubles.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from ai.config import get_settings
from ai.enums import DebateSide, Difficulty, Persona
from ai.llm_client import LLMClient, get_llm_client
from ai.memory import MEMORY_VERSION, DebateMemory, extract_memory, summarize_memory
from ai.models import ConversationTurn
from ai.persona_manager import get_persona_config
from ai.prompt_builder import build_messages
from ai.prompts.coaching import get_coaching_objective
from ai.response_parser import parse_llm_response

# Adaptation is optional — imported at module level to avoid circular imports
_adaptation = None


def _get_adaptation():
    global _adaptation
    if _adaptation is None:
        from ai import adaptation
        _adaptation = adaptation
    return _adaptation

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

    def __init__(self, llm_client: LLMClient | None = None, *, memory_limit: int = 3) -> None:
        self._llm = llm_client or get_llm_client()
        self._memory_limit = memory_limit

    async def generate_response(self, request: DebateRequest) -> DebateResponse:
        persona = get_persona_config(request.persona_id)
        s = get_settings()
        coaching = get_coaching_objective(request.round_number, request.persona_id.value)

        # --- Memory extraction ---
        memory_entries = extract_memory(request.history, persona=request.persona_id)
        memory_summary = summarize_memory(memory_entries, max_rounds=self._memory_limit)
        coaching_history = [e.coaching_skill for e in memory_entries]

        # --- Adaptive profiling ---
        profile = None
        adaptation_version = ""
        profile_reasoning = ""
        profile_challenge = ""
        profile_coaching = ""
        profile_confidence = 0.0

        if s.adaptive_personas:
            mod = _get_adaptation()
            if mod is not None:
                profile = mod.build_profile(memory_entries)
                adaptation_version = mod.ADAPTATION_VERSION
                profile_reasoning = profile.reasoning_level
                profile_challenge = profile.challenge_level
                profile_coaching = profile.coaching_style
                profile_confidence = profile.confidence

        messages = build_messages(
            persona=persona,
            topic=request.topic,
            side=request.side,
            difficulty=request.difficulty,
            round_number=request.round_number,
            history=request.history,
            user_argument=request.user_argument,
            memory_summary=memory_summary,
            profile=profile,
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
                "prompt_version=%s coaching=%s history_len=%d "
                "memory_version=%s memory_rounds=%d summary_len=%d coaching_history=%s "
                "adaptation_version=%s reasoning=%s challenge=%s coaching_style=%s confidence=%.2f "
                "prompt_len=%d response_ms=%d "
                "parse_ok=%s prompt_tokens=%d completion_tokens=%d total_tokens=%d",
                s.provider,
                s.model,
                request.persona_id.value,
                request.difficulty.value,
                request.round_number,
                persona.prompt_version,
                coaching.skill,
                len(request.history),
                MEMORY_VERSION,
                len(memory_entries),
                len(memory_summary),
                ",".join(coaching_history),
                adaptation_version,
                profile_reasoning,
                profile_challenge,
                profile_coaching,
                profile_confidence,
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
                "prompt_version=%s coaching=%s history_len=%d "
                "memory_version=%s memory_rounds=%d summary_len=%d coaching_history=%s "
                "adaptation_version=%s reasoning=%s challenge=%s coaching_style=%s confidence=%.2f "
                "prompt_len=%d response_ms=%d",
                s.provider,
                s.model,
                request.persona_id.value,
                request.difficulty.value,
                request.round_number,
                persona.prompt_version,
                coaching.skill,
                len(request.history),
                MEMORY_VERSION,
                len(memory_entries),
                len(memory_summary),
                ",".join(coaching_history),
                adaptation_version,
                profile_reasoning,
                profile_challenge,
                profile_coaching,
                profile_confidence,
                prompt_len,
                elapsed_ms,
            )
            raise
