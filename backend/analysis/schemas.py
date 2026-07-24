"""Analysis engine data models — strongly typed schemas for the analysis pipeline.

All models are Pydantic v2 for validation and serialization consistency.
The Observation model represents a single finding from any analyzer (evidence
quality, reasoning structure, fallacy detection, etc.). ReasoningScore provides
four numeric dimensions (0-1) with a computed overall average. AnalysisResult
aggregates everything into the final output shape sent to the frontend.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ObservationCategory(StrEnum):
    LOGIC = "logic"
    EVIDENCE = "evidence"
    CLARITY = "clarity"
    ASSUMPTION = "assumption"
    REBUTTAL = "rebuttal"
    STRENGTH = "strength"


class ObservationSeverity(StrEnum):
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class Observation(BaseModel):
    """A single finding from an analyzer."""
    category: ObservationCategory
    severity: ObservationSeverity
    message: str
    suggestion: str | None = None


class ReasoningScore(BaseModel):
    """Numeric scores for reasoning dimensions."""
    logical_validity: float = Field(ge=0.0, le=1.0, description="0-1: logical structure soundness")
    evidence_use: float = Field(ge=0.0, le=1.0, description="0-1: evidence quality and relevance")
    coherence: float = Field(ge=0.0, le=1.0, description="0-1: argument flow and readability")
    counterargument_readiness: float = Field(ge=0.0, le=1.0, description="0-1: vulnerability to opposition")

    @property
    def overall(self) -> float:
        return round(
            (self.logical_validity + self.evidence_use + self.coherence + self.counterargument_readiness) / 4,
            2,
        )


class AnalysisResult(BaseModel):
    """Complete analysis of a single debate argument."""
    observations: list[Observation] = Field(default_factory=list)
    scores: ReasoningScore = Field(default_factory=ReasoningScore)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    insight: str = Field(default="", description="One-line coaching insight")
    fallacies: list = Field(default_factory=list, description="Detected logical fallacies")
