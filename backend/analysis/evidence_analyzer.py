"""Evidence quality analyzer — evaluates the specificity and strength of claims."""

from __future__ import annotations

from abc import ABC, abstractmethod

from analysis.schemas import Observation


class EvidenceAnalyzer(ABC):
    """Interface for evidence quality analysis. Swap in Hugging Face models later."""

    @abstractmethod
    async def analyze(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> list[Observation]:
        ...


class HeuristicEvidenceAnalyzer(EvidenceAnalyzer):
    """Placeholder: checks for specificity markers and unsupported claims."""

    _VAGUE_MARKERS = {"everyone knows", "it's obvious", "clearly", "undoubtedly", "always", "never", "all", "none"}
    _SPECIFIC_MARKERS = {"percent", "%", "according to", "study", "research", "data", "survey", "report", "evidence"}

    async def analyze(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> list[Observation]:
        lower = user_argument.lower()
        observations: list[Observation] = []

        found_vague = [m for m in self._VAGUE_MARKERS if m in lower]
        if found_vague:
            observations.append(Observation(
                category="evidence",
                severity="warn",
                message=f"Vague generalizations detected: {', '.join(found_vague[:3])}.",
                suggestion="Replace absolute claims with qualified, evidence-backed statements.",
            ))

        found_specific = [m for m in self._SPECIFIC_MARKERS if m in lower]
        if not found_specific:
            observations.append(Observation(
                category="evidence",
                severity="info",
                message="No specific evidence references found.",
                suggestion="Cite data, studies, or concrete examples to support your claims.",
            ))

        return observations
