"""Fallacy taxonomy — definitions for detection and explanation."""

from __future__ import annotations

from dataclasses import dataclass

from analysis.fallacies.schemas import FallacyType


@dataclass(frozen=True)
class FallacyDefinition:
    type: FallacyType
    name: str
    description: str
    examples: tuple[str, ...]


TAXONOMY: dict[FallacyType, FallacyDefinition] = {
    FallacyType.HASTY_GENERALIZATION: FallacyDefinition(
        type=FallacyType.HASTY_GENERALIZATION,
        name="Hasty Generalization",
        description="Drawing a broad conclusion from too few or unrepresentative examples.",
        examples=(
            "Everyone I know hates AI, so AI must be universally hated.",
            "I met two rude people from that city, so everyone there is rude.",
        ),
    ),
    FallacyType.FALSE_DILEMMA: FallacyDefinition(
        type=FallacyType.FALSE_DILEMMA,
        name="False Dilemma",
        description="Presenting only two options when more exist.",
        examples=(
            "Either we ban all AI now or humanity is doomed.",
            "You're either with us or against us.",
        ),
    ),
    FallacyType.STRAW_MAN: FallacyDefinition(
        type=FallacyType.STRAW_MAN,
        name="Straw Man",
        description="Misrepresenting someone's argument to make it easier to attack.",
        examples=(
            "So you're saying we should just let AI do whatever it wants?",
            "You want to ban all technology, which is ridiculous.",
        ),
    ),
    FallacyType.APPEAL_TO_AUTHORITY: FallacyDefinition(
        type=FallacyType.APPEAL_TO_AUTHORITY,
        name="Appeal to Authority",
        description="Citing an authority figure as evidence when the authority is irrelevant or the claim needs independent support.",
        examples=(
            "Elon Musk said AI is dangerous, so it must be dangerous.",
            "A famous professor agrees with me, so I must be right.",
        ),
    ),
    FallacyType.SLIPPERY_SLOPE: FallacyDefinition(
        type=FallacyType.SLIPPERY_SLOPE,
        name="Slippery Slope",
        description="Assuming one event will inevitably lead to extreme consequences without justification.",
        examples=(
            "If we allow AI in schools, soon robots will replace all teachers.",
            "Once we start regulating AI, all innovation will stop.",
        ),
    ),
    FallacyType.CIRCULAR_REASONING: FallacyDefinition(
        type=FallacyType.CIRCULAR_REASONING,
        name="Circular Reasoning",
        description="Using the conclusion as a premise — the argument assumes what it tries to prove.",
        examples=(
            "AI is bad because it's harmful, and it's harmful because it's bad.",
            "This policy works because it's effective.",
        ),
    ),
}
