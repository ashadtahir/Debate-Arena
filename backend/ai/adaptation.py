"""Adaptive persona system — adjusts coaching and challenge level based on user ability.

Computes a DebateProfile from debate history signals (fallacy patterns, argument
characteristics, coaching trajectory). The profile drives prompt adaptation
without changing the user-facing difficulty setting.

Architecture: stateless. build_profile() takes memory entries and returns a
DebateProfile. No state is held between requests.

ADAPTATION_VERSION tracks the adaptation logic. Bump when the profiling
strategy changes materially.

Future: swap heuristic profiling for ML-based classification by implementing
the same build_profile() interface.
"""

from __future__ import annotations

from dataclasses import dataclass

ADAPTATION_VERSION = "1.0"


@dataclass(frozen=True)
class DebateProfile:
    """User's current debate profile, computed from history."""

    reasoning_level: str  # "beginner", "intermediate", "advanced"
    evidence_level: str  # "beginner", "intermediate", "advanced"
    challenge_level: str  # "gentle", "moderate", "intense"
    coaching_style: str  # "encouraging", "balanced", "demanding"
    confidence: float  # 0-1: how confident we are in the profile


def build_profile(entries: list) -> DebateProfile:
    """Compute a DebateProfile from memory entries.

    Uses available signals: detected fallacies, argument length, coaching history.
    Falls back to beginner defaults for empty histories.

    Future: add reasoning_scores to MemoryEntry for more accurate profiling.
    """
    if not entries:
        return _default_profile()

    # --- Signal extraction ---
    total_fallacies = sum(len(e.detected_fallacies) for e in entries)
    avg_arg_len = _avg_argument_length(entries)
    coaching_skills = [e.coaching_skill for e in entries]
    rounds_completed = len(entries)

    # --- Reasoning level ---
    reasoning = _infer_reasoning_level(total_fallacies, rounds_completed, avg_arg_len)

    # --- Evidence level ---
    total_evidence = sum(len(e.key_evidence) for e in entries)
    evidence = _infer_evidence_level(total_evidence, rounds_completed)

    # --- Derived levels ---
    challenge = _derive_challenge_level(reasoning, evidence)
    coaching = _derive_coaching_style(reasoning)
    confidence = _compute_confidence(rounds_completed, total_fallacies)

    return DebateProfile(
        reasoning_level=reasoning,
        evidence_level=evidence,
        challenge_level=challenge,
        coaching_style=coaching,
        confidence=confidence,
    )


def get_adaptation_guidance(profile: DebateProfile, persona_id: str) -> str:
    """Generate prompt guidance text from a profile for a specific persona."""
    level = profile.reasoning_level
    style = profile.coaching_style

    lines = [
        f"ADAPTIVE DIFFICULTY — user level: {level}, coaching: {style}:",
        _level_instruction(level),
        _persona_level_guidance(persona_id, level),
    ]

    if style == "encouraging":
        lines.append("Tone: supportive and encouraging. Acknowledge progress and effort.")
    elif style == "demanding":
        lines.append("Tone: rigorous and exacting. Do not accept weak reasoning.")
    else:
        lines.append("Tone: balanced. Challenge when needed, support when appropriate.")

    return "\n".join(lines)


# --- Heuristic inference functions ---

def _avg_argument_length(entries: list) -> float:
    lengths = [len(e.user_argument) for e in entries if e.user_argument]
    return sum(lengths) / len(lengths) if lengths else 0


def _infer_reasoning_level(fallacy_count: int, rounds: int, avg_len: float) -> str:
    """Infer reasoning level from fallacy frequency, round count, and argument length."""
    if rounds == 0:
        return "beginner"

    fallacies_per_round = fallacy_count / rounds

    # High fallacy rate = beginner
    if fallacies_per_round >= 2:
        return "beginner"
    # Low fallacy rate + long arguments = advanced
    if fallacies_per_round < 0.5 and avg_len > 300:
        return "advanced"
    # Moderate
    if fallacies_per_round < 1.0 and avg_len > 150:
        return "intermediate"
    return "beginner"


def _infer_evidence_level(total_evidence: int, rounds: int) -> str:
    """Infer evidence usage level from evidence markers found across rounds."""
    if rounds == 0:
        return "beginner"

    evidence_per_round = total_evidence / rounds

    if evidence_per_round >= 2:
        return "advanced"
    if evidence_per_round >= 1:
        return "intermediate"
    return "beginner"


def _derive_challenge_level(reasoning: str, evidence: str) -> str:
    """Derive challenge intensity from reasoning and evidence levels."""
    levels = {"beginner": 0, "intermediate": 1, "advanced": 2}
    avg = (levels.get(reasoning, 0) + levels.get(evidence, 0)) / 2

    if avg >= 1.5:
        return "intense"
    if avg >= 0.5:
        return "moderate"
    return "gentle"


def _derive_coaching_style(reasoning: str) -> str:
    """Derive coaching style from reasoning level."""
    if reasoning == "beginner":
        return "encouraging"
    if reasoning == "advanced":
        return "demanding"
    return "balanced"


def _compute_confidence(rounds: int, fallacies: int) -> float:
    """Confidence increases with more data (rounds)."""
    base = min(rounds / 3, 1.0)  # Full confidence at 3+ rounds
    return round(base, 2)


def _default_profile() -> DebateProfile:
    """Default profile for round 1 (no history)."""
    return DebateProfile(
        reasoning_level="beginner",
        evidence_level="beginner",
        challenge_level="gentle",
        coaching_style="encouraging",
        confidence=0.0,
    )


def _level_instruction(level: str) -> str:
    """General instruction for a difficulty level."""
    if level == "beginner":
        return (
            "Adapt for beginner: explain concepts clearly, ask simpler questions, "
            "encourage improvement. Avoid overwhelming criticism. Focus on one point at a time."
        )
    if level == "advanced":
        return (
            "Adapt for advanced: stress-test arguments, explore edge cases, "
            "use sophisticated counterexamples. Acknowledge strong reasoning before escalating."
        )
    return (
        "Adapt for intermediate: challenge assumptions, request stronger evidence, "
        "expose inconsistencies. Push for deeper reasoning."
    )


def _persona_level_guidance(persona_id: str, level: str) -> str:
    """Persona-specific adaptation for a difficulty level."""
    guidance = {
        "socrates": {
            "beginner": "Use short, guiding questions. Help them discover the answer through simple prompts.",
            "intermediate": "Ask probing questions that expose assumptions. Push for definitions and precision.",
            "advanced": "Use layered elenctic questioning. Guide them to deeper contradictions through Socratic chains.",
        },
        "prosecutor": {
            "beginner": "Ask for evidence on one claim at a time. Be encouraging when they provide support.",
            "intermediate": "Request evidence for multiple claims. Challenge inconsistencies between their points.",
            "advanced": "Cross-examine multiple claims simultaneously. Chain inconsistencies together into a case.",
        },
        "philosopher": {
            "beginner": "Clarify definitions together. Use simple thought experiments to test their position.",
            "intermediate": "Question assumptions and explore first principles. Use thought experiments.",
            "advanced": "Deploy sophisticated first-principles reasoning. Construct complex thought experiments that test every premise.",
        },
        "devils-advocate": {
            "beginner": "Introduce one counterpoint at a time. Be constructive in your pushback.",
            "intermediate": "Present stronger counter-positions. Test how they defend against multiple angles.",
            "advanced": "Present the strongest possible opposing position. Pressure-test every premise systematically.",
        },
    }
    return guidance.get(persona_id, {}).get(level, "")
