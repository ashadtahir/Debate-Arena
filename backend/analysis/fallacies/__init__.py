"""Fallacy detection module."""

from analysis.fallacies.detector import FallacyDetector, HeuristicFallacyDetector
from analysis.fallacies.schemas import Fallacy

__all__ = ["Fallacy", "FallacyDetector", "HeuristicFallacyDetector"]
