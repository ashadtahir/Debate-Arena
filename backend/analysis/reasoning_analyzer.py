"""Reasoning quality analyzer — checks logical structure of arguments."""

from __future__ import annotations

from abc import ABC, abstractmethod

from analysis.schemas import Observation, ReasoningScore


class ReasoningAnalyzer(ABC):
    """Interface for reasoning quality analysis. Swap in Hugging Face models later."""

    @abstractmethod
    async def analyze(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> tuple[ReasoningScore, list[Observation]]:
        ...


class HeuristicReasoningAnalyzer(ReasoningAnalyzer):
    """Placeholder: keyword-based heuristic reasoning checks."""

    _LOGICAL_MARKERS = {"because", "therefore", "however", "consequently", "since", "thus", "hence"}
    _EVIDENCE_MARKERS = {"study", "research", "data", "evidence", "report", "according to", "statistics", "survey"}
    _WEAK_MARKERS = {"i think", "i feel", "maybe", "probably", "sort of", "i guess", "believe"}

    async def analyze(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> tuple[ReasoningScore, list[Observation]]:
        lower = user_argument.lower()
        words = lower.split()
        word_count = len(words)

        has_logical = any(m in lower for m in self._LOGICAL_MARKERS)
        has_evidence = any(m in lower for m in self._EVIDENCE_MARKERS)
        has_weak = any(m in lower for m in self._WEAK_MARKERS)

        logical = min(1.0, 0.4 + (0.3 if has_logical else 0) + (0.15 if word_count > 30 else 0))
        evidence = min(1.0, 0.2 + (0.5 if has_evidence else 0) + (0.1 if word_count > 50 else 0))
        coherence = min(1.0, 0.3 + (0.25 if word_count > 20 else 0) + (0.2 if has_logical else 0))
        counter = min(1.0, 0.3 + (0.2 if "but" in lower or "however" in lower else 0) + (0.2 if has_evidence else 0))

        observations: list[Observation] = []

        if has_weak:
            observations.append(Observation(
                category="clarity",
                severity="warn",
                message="Argument contains hedging language (I think, maybe, probably).",
                suggestion="Replace hedging with declarative statements to strengthen your position.",
            ))

        if not has_logical:
            observations.append(Observation(
                category="logic",
                severity="info",
                message="No explicit logical connectors found (because, therefore, however).",
                suggestion="Use connectives to make your reasoning chain explicit.",
            ))

        if not has_evidence:
            observations.append(Observation(
                category="evidence",
                severity="info",
                message="No evidence markers detected (study, data, research, etc.).",
                suggestion="Ground your claims in specific evidence or examples.",
            ))

        if word_count < 15:
            observations.append(Observation(
                category="clarity",
                severity="warn",
                message=f"Argument is very short ({word_count} words).",
                suggestion="Expand your argument with supporting details or examples.",
            ))

        return (
            ReasoningScore(
                logical_validity=logical,
                evidence_use=evidence,
                coherence=coherence,
                counterargument_readiness=counter,
            ),
            observations,
        )
