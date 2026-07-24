"""Insight generator — synthesizes observations into coaching feedback.

The InsightGenerator ABC takes all observations and reasoning scores, then
produces a list of strengths, improvements, and a one-line coaching insight.

HeuristicInsightGenerator selects the strongest/weakest scores, prioritizes
high-severity observations, and generates a contextual insight based on the
argument's overall quality and the debate round.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from analysis.schemas import AnalysisResult, Observation, ReasoningScore


class InsightGenerator(ABC):
    """Interface for insight generation. Swap in LLM-backed implementations later."""

    @abstractmethod
    async def generate(
        self,
        *,
        user_argument: str,
        persona: str,
        difficulty: str,
        round_number: int,
        scores: ReasoningScore,
        observations: list[Observation],
    ) -> AnalysisResult:
        ...


class HeuristicInsightGenerator(InsightGenerator):
    """Placeholder: rule-based insight synthesis from observations and scores."""

    async def generate(
        self,
        *,
        user_argument: str,
        persona: str,
        difficulty: str,
        round_number: int,
        scores: ReasoningScore,
        observations: list[Observation],
    ) -> AnalysisResult:
        strengths: list[str] = []
        improvements: list[str] = []

        if scores.logical_validity >= 0.6:
            strengths.append("Clear logical structure with explicit reasoning chain.")
        else:
            improvements.append("Strengthen logical flow with connectives (because, therefore).")

        if scores.evidence_use >= 0.6:
            strengths.append("Good use of evidence to support claims.")
        else:
            improvements.append("Ground claims in specific evidence or examples.")

        if scores.coherence >= 0.6:
            strengths.append("Argument reads clearly and follows a coherent structure.")
        else:
            improvements.append("Improve argument flow — organize points in a clear sequence.")

        if scores.counterargument_readiness >= 0.6:
            strengths.append("Shows awareness of opposing perspectives.")
        else:
            improvements.append("Anticipate and address counterarguments proactively.")

        if not strengths:
            strengths.append("You showed up and made your case — that takes courage.")

        if not improvements:
            improvements.append("Consider raising the difficulty to challenge yourself further.")

        insight = _pick_insight(scores, round_number)

        return AnalysisResult(
            observations=observations,
            scores=scores,
            strengths=strengths,
            improvements=improvements,
            insight=insight,
        )


def _pick_insight(scores: ReasoningScore, round_number: int) -> str:
    overall = scores.overall
    if overall >= 0.75:
        return "Strong argument. Push for deeper specificity in the next round."
    if overall >= 0.5:
        return "Solid foundation — tighten your evidence and logical connectives."
    if overall >= 0.3:
        return "Room to grow: focus on one clear claim backed by one piece of evidence."
    return "Start with a single, specific claim and build from there."
