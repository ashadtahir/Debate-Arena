"""Prompt builder — structured section-based prompt composition.

Assembles the system prompt from discrete sections:
  Role → Strategy → Mission → Universal Rules → Coaching Goal → Debate Context → Response Structure → Format

Uses PromptContext internally to reduce parameter sprawl. The public API
(build_messages) signature is unchanged.

Each section is built independently, making prompt iteration and debugging
straightforward — just inspect the output without needing to hit the LLM.

PROMPT_VERSION = "2.0" is defined in prompts/base.py and tracked in logs.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.enums import DebateSide, Difficulty
from ai.models import ConversationTurn
from ai.persona_manager import PersonaConfig
from ai.prompts.base import (
    DIFFICULTY_INSTRUCTIONS,
    GLOBAL_DEBATE_RULES,
    RESPONSE_FORMAT_INSTRUCTIONS,
    RESPONSE_STRUCTURE,
    ROUND_LABELS,
)
from ai.prompts.coaching import get_coaching_objective

# Adaptation is optional — imported at module level to avoid circular imports
_adaptation_module = None


def _get_adaptation():
    global _adaptation_module
    if _adaptation_module is None:
        from ai import adaptation
        _adaptation_module = adaptation
    return _adaptation_module


@dataclass
class PromptContext:
    """Bundles all inputs for prompt composition. Reduces parameter sprawl."""

    persona: PersonaConfig
    topic: str
    side: DebateSide
    difficulty: Difficulty
    round_number: int
    history: list[ConversationTurn]
    user_argument: str
    memory_summary: str = ""
    profile: object | None = None  # DebateProfile from adaptation module


def _section_role(ctx: PromptContext) -> str:
    return ctx.persona.sections.role


def _section_strategy(ctx: PromptContext) -> str:
    return ctx.persona.sections.strategy


def _section_mission(ctx: PromptContext) -> str:
    return ctx.persona.sections.mission


def _section_rules(ctx: PromptContext) -> str:
    return GLOBAL_DEBATE_RULES


def _section_behavior(ctx: PromptContext) -> str:
    return ctx.persona.sections.behavior


def _section_constraints(ctx: PromptContext) -> str:
    return ctx.persona.sections.constraints


def _section_coaching(ctx: PromptContext) -> str:
    obj = get_coaching_objective(ctx.round_number, ctx.persona.id.value)
    lines = [
        f"COACHING OBJECTIVE — develop the user's {obj.skill} this round:",
        obj.instruction,
    ]
    if obj.persona_guidance:
        lines.append(f"Persona-specific approach: {obj.persona_guidance}")
    return "\n".join(lines)


def _section_adaptation(ctx: PromptContext) -> str:
    """Inject adaptive difficulty guidance if a profile is available."""
    if ctx.profile is None:
        return ""
    mod = _get_adaptation()
    if mod is None:
        return ""
    return mod.get_adaptation_guidance(ctx.profile, ctx.persona.id.value)


def _section_debate_context(ctx: PromptContext) -> str:
    stance_label = "defending" if ctx.side == DebateSide.FOR else "challenging"
    round_label = ROUND_LABELS.get(ctx.round_number, f"Round {ctx.round_number}")
    diff_block = DIFFICULTY_INSTRUCTIONS.get(ctx.difficulty.value, "")
    return (
        f"DEBATE CONTEXT:\n"
        f'Proposition: "{ctx.topic}"\n'
        f"The user is {stance_label} this proposition.\n"
        f"Current round: {ctx.round_number} — {round_label}\n\n"
        f"{diff_block}"
    )


def _section_memory(ctx: PromptContext) -> str:
    if not ctx.memory_summary:
        return ""
    return (
        f"PREVIOUS DEBATE CONTEXT (summarized from {ctx.round_number - 1} prior rounds):\n"
        f"{ctx.memory_summary}"
    )


def _section_response_structure() -> str:
    return RESPONSE_STRUCTURE


def _section_format() -> str:
    return RESPONSE_FORMAT_INSTRUCTIONS


def _section_history(history: list[ConversationTurn]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for entry in history:
        role = "assistant" if entry.speaker == "ai" else "user"
        messages.append({"role": role, "content": entry.content})
    return messages


def build_messages(
    persona: PersonaConfig,
    topic: str,
    side: DebateSide,
    difficulty: Difficulty,
    round_number: int,
    history: list[ConversationTurn],
    user_argument: str,
    *,
    memory_summary: str = "",
    profile: object | None = None,
) -> list[dict[str, str]]:
    """Construct the full message list for the LLM."""

    ctx = PromptContext(
        persona=persona,
        topic=topic,
        side=side,
        difficulty=difficulty,
        round_number=round_number,
        history=history,
        user_argument=user_argument,
        memory_summary=memory_summary,
        profile=profile,
    )

    system_sections = [
        _section_role(ctx),
        _section_strategy(ctx),
        _section_mission(ctx),
        _section_rules(ctx),
        _section_behavior(ctx),
        _section_coaching(ctx),
    ]

    adaptation_section = _section_adaptation(ctx)
    if adaptation_section:
        system_sections.append(adaptation_section)

    system_sections.append(_section_debate_context(ctx))

    memory_section = _section_memory(ctx)
    if memory_section:
        system_sections.append(memory_section)

    system_sections.extend([
        _section_response_structure(),
        _section_format(),
    ])

    full_system = "\n\n---\n\n".join(system_sections)

    messages: list[dict[str, str]] = [
        {"role": "system", "content": full_system},
    ]
    messages.extend(_section_history(ctx.history))
    messages.append({"role": "user", "content": ctx.user_argument})

    return messages
