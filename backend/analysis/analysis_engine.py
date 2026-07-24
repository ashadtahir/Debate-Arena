"""Analysis engine — orchestrates the full analysis pipeline.

Runs four analyzers in sequence via dependency injection:
1. ReasoningAnalyzer → scores (logical_validity, evidence_use, coherence, counterargument_readiness)
2. EvidenceAnalyzer → observations about evidence quality
3. FallacyDetector → confidence-scored fallacy detections
4. InsightGenerator → synthesizes everything into strengths, improvements, and coaching insight

All analyzers are ABCs with heuristic defaults. Swap in Hugging Face models
by passing custom implementations to the constructor:
    engine = AnalysisEngine(reasoning=HFReasoningAnalyzer())
"""

from __future__ import annotations

from dataclasses import dataclass, field

from analysis.evidence_analyzer import EvidenceAnalyzer, HeuristicEvidenceAnalyzer
from analysis.fallacies.detector import FallacyDetector, HeuristicFallacyDetector
from analysis.insight_generator import HeuristicInsightGenerator, InsightGenerator
from analysis.reasoning_analyzer import HeuristicReasoningAnalyzer, ReasoningAnalyzer
from analysis.schemas import AnalysisResult, Observation


@dataclass
class AnalysisEngine:
    """Stateless analysis engine. Accepts pluggable analyzers via constructor (dependency injection)."""

    reasoning: ReasoningAnalyzer = field(default_factory=HeuristicReasoningAnalyzer)
    evidence: EvidenceAnalyzer = field(default_factory=HeuristicEvidenceAnalyzer)
    fallacies: FallacyDetector = field(default_factory=HeuristicFallacyDetector)
    insight: InsightGenerator = field(default_factory=HeuristicInsightGenerator)

    async def analyze(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> AnalysisResult:
        scores, reasoning_obs = await self.reasoning.analyze(
            user_argument,
            persona=persona,
            difficulty=difficulty,
            round_number=round_number,
        )

        evidence_obs = await self.evidence.analyze(
            user_argument,
            persona=persona,
            difficulty=difficulty,
            round_number=round_number,
        )

        detected_fallacies = await self.fallacies.detect(
            user_argument,
            persona=persona,
            difficulty=difficulty,
            round_number=round_number,
        )

        all_observations: list[Observation] = reasoning_obs + evidence_obs

        result = await self.insight.generate(
            user_argument=user_argument,
            persona=persona,
            difficulty=difficulty,
            round_number=round_number,
            scores=scores,
            observations=all_observations,
        )

        result.fallacies = detected_fallacies

        return result
