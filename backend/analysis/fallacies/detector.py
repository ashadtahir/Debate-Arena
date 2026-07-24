"""Fallacy detector — abstract interface and default heuristic implementation.

The FallacyDetector ABC exposes a single `detect()` method that returns a list
of Fallacy objects, each with a confidence score (0-1), explanation, and the
text evidence that triggered detection.

HeuristicFallacyDetector runs six independent fallacy detectors (hasty
generalization, false dilemma, straw man, appeal to authority, slippery slope,
circular reasoning), each combining structural, language, reasoning, and
semantic features into confidence scores. Results are sorted by confidence.

To swap in a Hugging Face classifier, implement FallacyDetector and pass it
to AnalysisEngine(fallacies=YourClassifier()).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from analysis.features import ArgumentFeatures, extract_all
from analysis.fallacies.heuristics import ALL_DETECTORS
from analysis.fallacies.schemas import Fallacy


class FallacyDetector(ABC):
    """Interface for fallacy detection. Swap in Hugging Face classifiers later."""

    @abstractmethod
    async def detect(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> list[Fallacy]:
        ...


class HeuristicFallacyDetector(FallacyDetector):
    """Default detector: multi-signal heuristic scoring per fallacy type.

    Each fallacy detector extracts structural, language, reasoning, and semantic
    features independently, then combines them into a confidence score.  No single
    signal dominates — this avoids both false positives from keyword matching and
    missed fallacies from purely semantic approaches.
    """

    async def detect(
        self,
        user_argument: str,
        *,
        persona: str,
        difficulty: str,
        round_number: int,
    ) -> list[Fallacy]:
        features = extract_all(user_argument)
        fallacies: list[Fallacy] = []

        for detector_fn in ALL_DETECTORS:
            result = detector_fn(user_argument, features)
            if result is not None:
                fallacies.append(result)

        fallacies.sort(key=lambda f: f.confidence, reverse=True)
        return fallacies
