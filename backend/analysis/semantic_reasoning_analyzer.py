"""Semantic reasoning analyzer — multi-signal feature extraction + weighted scoring.

MiniLM embeddings are used as semantic features (topic consistency, reference
retrieval), NOT as direct reasoning scores. Semantic similarity alone is a poor
proxy for reasoning quality — a well-written but wrong argument can have high
similarity to a reference. The analyzer extracts structural, reasoning, evidence,
language, and semantic features independently, then combines them via weighted
scoring to produce robust ReasoningScore values.
"""

from __future__ import annotations

import logging
import re

from analysis.features import ArgumentFeatures, extract_all
from analysis.reasoning_analyzer import ReasoningAnalyzer
from analysis.schemas import Observation, ReasoningScore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights — tuned so no single feature dominates
# ---------------------------------------------------------------------------

_W_LOGICAL_STRUCT = 0.25
_W_LOGICAL_REASON = 0.35
_W_LOGICAL_SEMANTIC = 0.25
_W_LOGICAL_LANG = 0.15

_W_EVIDENCE_EVID = 0.45
_W_EVIDENCE_SEMANTIC = 0.25
_W_EVIDENCE_STRUCT = 0.15
_W_EVIDENCE_REASON = 0.15

_W_COHERENCE_STRUCT = 0.3
_W_COHERENCE_SEMANTIC = 0.35
_W_COHERENCE_LANG = 0.2
_W_COHERENCE_REASON = 0.15

_W_COUNTER_REASON = 0.4
_W_COUNTER_SEMANTIC = 0.35
_W_COUNTER_LANG = 0.15
_W_COUNTER_STRUCT = 0.1


class SemanticReasoningAnalyzer(ReasoningAnalyzer):
    """Scores reasoning dimensions by combining multiple independent feature signals."""

    async def analyze(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> tuple[ReasoningScore, list[Observation]]:
        features = extract_all(user_argument)

        logical = self._score_logical(features)
        evidence = self._score_evidence(features)
        coherence = self._score_coherence(features)
        counter = self._score_counterargument(features)

        score = ReasoningScore(
            logical_validity=round(max(0.0, min(1.0, logical)), 2),
            evidence_use=round(max(0.0, min(1.0, evidence)), 2),
            coherence=round(max(0.0, min(1.0, coherence)), 2),
            counterargument_readiness=round(max(0.0, min(1.0, counter)), 2),
        )

        observations = _build_observations(features)

        logger.info(
            "Semantic reasoning: logical=%.2f evidence=%.2f coherence=%.2f counter=%.2f "
            "structural=%.2f reasoning=%.2f evidence_feat=%.2f language=%.2f semantic=%.2f",
            score.logical_validity, score.evidence_use, score.coherence, score.counterargument_readiness,
            features.structural.score, features.reasoning.score,
            features.evidence.score, features.language.score, features.semantic.score,
        )

        return score, observations

    @staticmethod
    def _score_logical(f: ArgumentFeatures) -> float:
        return (
            f.structural.score * _W_LOGICAL_STRUCT
            + f.reasoning.score * _W_LOGICAL_REASON
            + f.semantic.logical_similarity * _W_LOGICAL_SEMANTIC
            + f.language.score * _W_LOGICAL_LANG
        )

    @staticmethod
    def _score_evidence(f: ArgumentFeatures) -> float:
        return (
            f.evidence.score * _W_EVIDENCE_EVID
            + f.semantic.evidence_similarity * _W_EVIDENCE_SEMANTIC
            + f.structural.score * _W_EVIDENCE_STRUCT
            + f.reasoning.score * _W_EVIDENCE_REASON
        )

    @staticmethod
    def _score_coherence(f: ArgumentFeatures) -> float:
        return (
            f.structural.score * _W_COHERENCE_STRUCT
            + f.semantic.coherence_similarity * _W_COHERENCE_SEMANTIC
            + f.language.score * _W_COHERENCE_LANG
            + f.reasoning.score * _W_COHERENCE_REASON
        )

    @staticmethod
    def _score_counterargument(f: ArgumentFeatures) -> float:
        return (
            f.reasoning.score * _W_COUNTER_REASON
            + f.semantic.counter_similarity * _W_COUNTER_SEMANTIC
            + f.language.score * _W_COUNTER_LANG
            + f.structural.score * _W_COUNTER_STRUCT
        )


def _build_observations(f: ArgumentFeatures) -> list[Observation]:
    obs: list[Observation] = []

    if f.language.hedging_count > 0:
        obs.append(Observation(
            category="clarity",
            severity="warn",
            message=f"Argument contains {f.language.hedging_count} hedging expression(s).",
            suggestion="Replace hedging with declarative statements to strengthen your position.",
        ))

    if f.reasoning.connector_count == 0:
        obs.append(Observation(
            category="logic",
            severity="info",
            message="No logical connectors detected (because, therefore, however).",
            suggestion="Use connectives to make your reasoning chain explicit.",
        ))

    if not f.reasoning.has_premise:
        obs.append(Observation(
            category="logic",
            severity="info",
            message="No explicit premise indicators found (because, since, given that).",
            suggestion="State your premises clearly before drawing conclusions.",
        ))

    if f.evidence.named_entity_count == 0 and not f.evidence.has_statistics:
        obs.append(Observation(
            category="evidence",
            severity="info",
            message="No specific entities or statistics detected.",
            suggestion="Ground your claims in concrete examples, data, or named references.",
        ))

    if not f.reasoning.has_counterargument:
        obs.append(Observation(
            category="rebuttal",
            severity="info",
            message="Argument does not acknowledge opposing views.",
            suggestion="Anticipate counterarguments and address them proactively.",
        ))

    if f.structural.word_count < 15:
        obs.append(Observation(
            category="clarity",
            severity="warn",
            message=f"Argument is very short ({f.structural.word_count} words).",
            suggestion="Expand your argument with supporting details or examples.",
        ))

    if f.language.repetition_score > 0.3:
        obs.append(Observation(
            category="clarity",
            severity="warn",
            message="Argument shows significant word repetition.",
            suggestion="Vary your vocabulary and sentence structure for better readability.",
        ))

    return obs
