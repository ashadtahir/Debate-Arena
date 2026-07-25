"""Debate memory — extracts and summarizes key information from conversation history.

The memory system gives the LLM context about previous rounds without feeding
it the full transcript. Each round is distilled into structured entries
(claims, evidence, fallacies, coaching focus) and summarized into a compact
text block for the prompt.

MEMORY_VERSION tracks the memory extraction logic. Bump when the extraction
or summarization strategy changes materially.

Architecture: stateless. `extract_memory` takes a list of ConversationTurns
and returns structured entries. `summarize_memory` condenses entries into
prompt-ready text. No state is held between requests — the DebateEngine
computes memory from the incoming history each time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ai.enums import Persona
from ai.models import ConversationTurn
from ai.prompts.coaching import get_coaching_objective

MEMORY_VERSION = "1.0"


@dataclass
class MemoryEntry:
    """Structured memory for a single debate round."""

    round: int
    user_argument: str
    ai_response: str
    persona: Persona
    coaching_skill: str
    key_claims: list[str] = field(default_factory=list)
    key_evidence: list[str] = field(default_factory=list)
    detected_fallacies: list[str] = field(default_factory=list)
    reasoning_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class DebateMemory:
    """Aggregated memory across all completed rounds."""

    entries: list[MemoryEntry] = field(default_factory=list)
    version: str = MEMORY_VERSION

    @property
    def round_count(self) -> int:
        return len(self.entries)

    @property
    def coaching_history(self) -> list[str]:
        return [e.coaching_skill for e in self.entries]

    def summary(self) -> str:
        """Condensed text block for the prompt. Empty if no entries."""
        if not self.entries:
            return ""

        lines: list[str] = []
        for e in self.entries:
            parts = [f"Round {e.round} ({e.coaching_skill})"]
            if e.key_claims:
                parts.append(f"Claims: {'; '.join(e.key_claims)}")
            if e.key_evidence:
                parts.append(f"Evidence: {'; '.join(e.key_evidence)}")
            if e.detected_fallacies:
                parts.append(f"Fallacies: {', '.join(e.detected_fallacies)}")
            lines.append(" | ".join(parts))

        return "\n".join(lines)


# --- Claim extraction heuristic (no LLM call) ---

_CLAIM_MARKERS = re.compile(
    r"(?:"
    r"(?:I (?:believe|think|argue|claim|maintain|assert))|"
    r"(?:it(?:'s| is) (?:clear|obvious|undeniable|certain))|"
    r"(?:the (?:evidence|data|facts?) (?:shows?|indicates?|proves?))|"
    r"(?:studies (?:show|suggest|indicate))|"
    r"(?:in (?:my opinion|my view))|"
    r"(?:fundamentally|essentially|obviously|clearly)"
    r")",
    re.IGNORECASE,
)

_EVIDENCE_MARKERS = re.compile(
    r"(?:"
    r"\d+%|"
    r"(?:according to|research shows|studies show|data suggests)|"
    r"(?:for example|for instance|such as)|"
    r"(?:evidence|statistics|data|findings|reports?|surveys?)|"
    r"(?:university|institute|journal|study|report)"
    r")",
    re.IGNORECASE,
)

_FALLACY_PATTERNS: dict[str, re.Pattern[str]] = {
    "hasty_generalization": re.compile(r"\b(?:all|every|always|never|nobody|everyone|no one)\b", re.IGNORECASE),
    "false_dilemma": re.compile(r"\b(?:either|or else|only two|no other option|must choose)\b", re.IGNORECASE),
    "straw_man": re.compile(r"\b(?:so you'?re saying|what you'?re really|in other words)\b", re.IGNORECASE),
    "appeal_to_authority": re.compile(r"\b(?:expert|authority|specialist|professional|scientist)\b", re.IGNORECASE),
    "slippery_slope": re.compile(r"\b(?:will inevitably|lead to|next thing|eventually|before long)\b", re.IGNORECASE),
    "circular_reasoning": re.compile(r"\b(?:because it is|it's true because|obviously|self-evident)\b", re.IGNORECASE),
}


def _extract_claims(text: str) -> list[str]:
    """Extract key claim phrases from argument text."""
    claims: list[str] = []
    for match in _CLAIM_MARKERS.finditer(text):
        start = max(0, match.start() - 20)
        end = min(len(text), match.end() + 40)
        snippet = text[start:end].strip()
        if snippet and len(snippet) > 10:
            claims.append(snippet)
    return claims[:3]  # Cap at 3 per round


def _extract_evidence(text: str) -> list[str]:
    """Extract evidence phrases from argument text."""
    evidence: list[str] = []
    for match in _EVIDENCE_MARKERS.finditer(text):
        start = max(0, match.start() - 20)
        end = min(len(text), match.end() + 40)
        snippet = text[start:end].strip()
        if snippet and len(snippet) > 10:
            evidence.append(snippet)
    return evidence[:3]  # Cap at 3 per round


def _extract_fallacies(text: str) -> list[str]:
    """Detect potential fallacy patterns in text."""
    detected: list[str] = []
    for fallacy_type, pattern in _FALLACY_PATTERNS.items():
        if pattern.search(text):
            detected.append(fallacy_type)
    return detected


def extract_memory(
    history: list[ConversationTurn],
    *,
    persona: Persona,
) -> list[MemoryEntry]:
    """Process raw conversation history into structured memory entries.

    Each pair of (user message, AI response) becomes one MemoryEntry.
    Claims, evidence, and fallacies are extracted via regex heuristics.
    """
    entries: list[MemoryEntry] = []

    # Pair up user/ai turns. History alternates: user, ai, user, ai, ...
    # We need to handle the case where history ends with the user's latest message
    # (which hasn't gotten an AI response yet).
    pairs: list[tuple[ConversationTurn, ConversationTurn | None]] = []
    i = 0
    while i < len(history):
        turn = history[i]
        if turn.speaker == "user" or turn.speaker != persona.value:
            # This is a user turn. Next might be AI response.
            ai_turn = None
            if i + 1 < len(history) and history[i + 1].speaker != "user":
                ai_turn = history[i + 1]
                i += 2
            else:
                i += 1
            pairs.append((turn, ai_turn))
        else:
            # Stray AI message (shouldn't happen, skip)
            i += 1

    for round_idx, (user_turn, ai_turn) in enumerate(pairs, start=1):
        user_text = user_turn.content
        ai_text = ai_turn.content if ai_turn else ""

        coaching = get_coaching_objective(round_idx, persona.value)

        entry = MemoryEntry(
            round=round_idx,
            user_argument=user_text,
            ai_response=ai_text,
            persona=persona,
            coaching_skill=coaching.skill,
            key_claims=_extract_claims(user_text),
            key_evidence=_extract_evidence(user_text),
            detected_fallacies=_extract_fallacies(user_text),
        )
        entries.append(entry)

    return entries


def summarize_memory(entries: list[MemoryEntry], max_rounds: int = 3) -> str:
    """Condense memory entries into a prompt-ready summary.

    Only includes the most recent `max_rounds` entries to control prompt length.
    """
    recent = entries[-max_rounds:] if len(entries) > max_rounds else entries
    memory = DebateMemory(entries=recent)
    return memory.summary()
