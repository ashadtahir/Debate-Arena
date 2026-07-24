"""Shared Pydantic models used across the debate system."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ai.enums import DebateSide, Difficulty, Persona


class ConversationTurn(BaseModel):
    """A single turn in the debate conversation."""
    speaker: Persona | str = Field(..., description="'user' or a Persona enum value")
    content: str = Field(..., min_length=1)
