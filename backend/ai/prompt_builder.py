"""Builds structured prompts for the debate engine from context + persona config."""

from __future__ import annotations

from ai.enums import DebateSide, Difficulty
from ai.models import ConversationTurn
from ai.persona_manager import PersonaConfig
from ai.prompts.base import GLOBAL_DEBATE_RULES, RESPONSE_FORMAT_INSTRUCTIONS

ROUND_LABELS: dict[int, str] = {
    1: "Opening Arguments",
    2: "Rebuttal",
    3: "Counter-Rebuttal",
    4: "Final Challenge",
    5: "Closing Statements",
}

DIFFICULTY_INSTRUCTIONS: dict[Difficulty, str] = {
    Difficulty.APPRENTICE: (
        "DEBATE DIFFICULTY: Apprentice.\n"
        "Be measured and accessible. Focus on one key point per round. "
        "Your pushback should be clear but not overwhelming. "
        "Help the debater learn by asking focused questions."
    ),
    Difficulty.SCHOLAR: (
        "DEBATE DIFFICULTY: Scholar.\n"
        "Be sharper and more analytical. Challenge multiple points if justified. "
        "Use evidence-based reasoning and demand the same from your opponent. "
        "Push harder on logical inconsistencies."
    ),
    Difficulty.MASTER: (
        "DEBATE DIFFICULTY: Master.\n"
        "Be relentless. No easy wins. Explores every weakness in the argument. "
        "Demand rigorous evidence and precise reasoning. "
        "Your questions should be difficult to answer without deep thought."
    ),
}


def _section_debate_context(topic: str, side: DebateSide, round_number: int) -> str:
    stance_label = "defending" if side == DebateSide.FOR else "challenging"
    round_label = ROUND_LABELS.get(round_number, f"Round {round_number}")
    return (
        f"DEBATE CONTEXT:\n"
        f'Proposition: "{topic}"\n'
        f"The user is {stance_label} this proposition.\n"
        f"Current round: {round_number} — {round_label}"
    )


def _section_system_prompt(persona: PersonaConfig) -> str:
    return (
        f"{persona.system_prompt}\n\n"
        f"---\n\n"
        f"{RESPONSE_FORMAT_INSTRUCTIONS}\n\n"
        f"---\n\n"
        f"{GLOBAL_DEBATE_RULES}"
    )


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
) -> list[dict[str, str]]:
    """Construct the full message list for the LLM."""

    system_prompt = _section_system_prompt(persona)
    context = _section_debate_context(topic, side, round_number)
    diff_block = DIFFICULTY_INSTRUCTIONS[difficulty]

    full_system = f"{system_prompt}\n\n{context}\n\n{diff_block}"

    messages: list[dict[str, str]] = [
        {"role": "system", "content": full_system},
    ]
    messages.extend(_section_history(history))
    messages.append({"role": "user", "content": user_argument})

    return messages
