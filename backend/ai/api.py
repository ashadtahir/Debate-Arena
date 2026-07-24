"""Debate API endpoint."""

from __future__ import annotations

from fastapi import HTTPException
from pydantic import BaseModel, Field

from ai.debate_engine import DebateEngine, DebateRequest
from ai.enums import DebateSide, Difficulty, Persona
from ai.models import ConversationTurn
from ai.persona_manager import get_persona_config


class DebateRespondRequest(BaseModel):
    persona_id: Persona = Field(..., description="Persona ID: socrates, prosecutor, philosopher, devils-advocate")
    topic: str = Field(..., description="The debate proposition")
    side: DebateSide = Field(..., description="'for' or 'against'")
    difficulty: Difficulty = Field(..., description="apprentice, scholar, or master")
    round_number: int = Field(..., ge=1, le=5, description="Current round number (1-5)")
    history: list[ConversationTurn] = Field(default_factory=list, description="Previous messages in this debate")
    user_argument: str = Field(..., description="The user's latest argument")


class DebateRespondResponse(BaseModel):
    response: str
    thinking_style: str
    next_focus: str
    tone: str
    persona_id: str
    round_number: int
    parse_success: bool


class ErrorResponse(BaseModel):
    error: str


_engine = DebateEngine()


async def debate_respond(request: DebateRespondRequest) -> DebateRespondResponse:
    """POST /api/debate/respond — Generate an AI debate response."""
    try:
        get_persona_config(request.persona_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await _engine.generate_response(
        DebateRequest(
            persona_id=request.persona_id,
            topic=request.topic,
            side=request.side,
            difficulty=request.difficulty,
            round_number=request.round_number,
            history=request.history,
            user_argument=request.user_argument,
        )
    )

    return DebateRespondResponse(
        response=result.response,
        thinking_style=result.thinking_style,
        next_focus=result.next_focus,
        tone=result.tone,
        persona_id=result.persona_id.value if hasattr(result.persona_id, 'value') else str(result.persona_id),
        round_number=result.round_number,
        parse_success=result.parse_success,
    )
