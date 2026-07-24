"""Fallacy schemas."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class FallacyType(StrEnum):
    HASTY_GENERALIZATION = "hasty_generalization"
    FALSE_DILEMMA = "false_dilemma"
    STRAW_MAN = "straw_man"
    APPEAL_TO_AUTHORITY = "appeal_to_authority"
    SLIPPERY_SLOPE = "slippery_slope"
    CIRCULAR_REASONING = "circular_reasoning"


class Fallacy(BaseModel):
    """A detected logical fallacy with explanation and optional text span."""
    type: FallacyType
    name: str
    confidence: float = Field(ge=0.0, le=1.0, description="0-1: detection confidence")
    explanation: str = Field(description="Why this is a fallacy")
    evidence: str = Field(description="The specific text that triggered detection")
    span_start: int | None = Field(default=None, description="Start char index (future highlighting)")
    span_end: int | None = Field(default=None, description="End char index (future highlighting)")
