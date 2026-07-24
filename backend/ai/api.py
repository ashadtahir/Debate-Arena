"""Debate API endpoint."""

from __future__ import annotations

import logging
import time

from fastapi import HTTPException
from pydantic import BaseModel, Field

from ai.debate_engine import DebateEngine, DebateRequest
from ai.enums import DebateSide, Difficulty, Persona
from ai.models import ConversationTurn
from ai.persona_manager import get_persona_config
from analysis.analysis_engine import AnalysisEngine
from analysis.schemas import AnalysisResult

logger = logging.getLogger(__name__)


class DebateRespondRequest(BaseModel):
    persona_id: Persona = Field(..., description="Persona ID: socrates, prosecutor, philosopher, devils-advocate")
    topic: str = Field(..., description="The debate proposition")
    side: DebateSide = Field(..., description="'for' or 'against'")
    difficulty: Difficulty = Field(..., description="apprentice, scholar, or master")
    round_number: int = Field(..., ge=1, le=5, description="Current round number (1-5)")
    history: list[ConversationTurn] = Field(default_factory=list, description="Previous messages in this debate")
    user_argument: str = Field(..., description="The user's latest argument")


class ReasoningScores(BaseModel):
    overall: float
    logic: float
    evidence: float
    coherence: float
    persuasion: float


class AnalysisObservation(BaseModel):
    type: str
    title: str
    description: str


class FallacyResult(BaseModel):
    type: str
    name: str
    confidence: float
    explanation: str
    evidence: str


class AnalysisSection(BaseModel):
    scores: ReasoningScores
    observations: list[AnalysisObservation]
    fallacies: list[FallacyResult]
    strengths: list[str]
    improvements: list[str]
    insight: str


class DebateRespondResponse(BaseModel):
    response: str
    thinking_style: str
    next_focus: str
    tone: str
    persona_id: str
    round_number: int
    parse_success: bool
    analysis: AnalysisSection | None = None


class ErrorResponse(BaseModel):
    error: str


_debate_engine = DebateEngine()
_analysis_engine = AnalysisEngine()


def _map_analysis(result: AnalysisResult, difficulty: str) -> AnalysisSection:
    scores = result.scores
    return AnalysisSection(
        scores=ReasoningScores(
            overall=round(scores.overall * 100),
            logic=round(scores.logical_validity * 100),
            evidence=round(scores.evidence_use * 100),
            coherence=round(scores.coherence * 100),
            persuasion=round(scores.counterargument_readiness * 100),
        ),
        observations=[
            AnalysisObservation(
                type=_map_obs_type(o.category.value, o.severity.value),
                title=o.category.value.replace("_", " ").title(),
                description=o.message + (f" {o.suggestion}" if o.suggestion else ""),
            )
            for o in result.observations
        ],
        fallacies=[
            FallacyResult(
                type=f.type.value if hasattr(f.type, "value") else str(f.type),
                name=f.name,
                confidence=round(f.confidence, 2),
                explanation=f.explanation,
                evidence=f.evidence,
            )
            for f in result.fallacies
        ],
        strengths=result.strengths,
        improvements=result.improvements,
        insight=result.insight,
    )


def _map_obs_type(category: str, severity: str) -> str:
    if category == "strength":
        return "strength"
    if category == "rebuttal" or severity == "critical":
        return "fallacy"
    return "suggestion"


async def debate_respond(request: DebateRespondRequest) -> DebateRespondResponse:
    """POST /api/debate/respond — Generate an AI debate response with live analysis."""
    try:
        get_persona_config(request.persona_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # --- Debate response ---
    debate_start = time.monotonic()
    result = await _debate_engine.generate_response(
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
    debate_ms = round((time.monotonic() - debate_start) * 1000)

    # --- Analysis (best-effort, never blocks debate response) ---
    analysis_section: AnalysisSection | None = None
    analysis_ms = 0
    fallacy_count = 0

    try:
        analysis_start = time.monotonic()
        analysis_result = await _analysis_engine.analyze(
            request.user_argument,
            persona=request.persona_id.value,
            difficulty=request.difficulty.value,
            round_number=request.round_number,
        )
        analysis_ms = round((time.monotonic() - analysis_start) * 1000)
        analysis_section = _map_analysis(analysis_result, request.difficulty.value)
        fallacy_count = len(analysis_result.fallacies)
    except Exception:
        analysis_ms = round((time.monotonic() - analysis_start) * 1000)
        logger.exception("Analysis failed: persona=%s round=%d analysis_ms=%d", request.persona_id.value, request.round_number, analysis_ms)

    total_ms = round((time.monotonic() - debate_start) * 1000)

    logger.info(
        "persona=%s round=%d topic=%s difficulty=%s "
        "debate_ms=%d analysis_ms=%d total_ms=%d "
        "parse_ok=%s fallacies=%d",
        request.persona_id.value,
        request.round_number,
        request.topic[:40],
        request.difficulty.value,
        debate_ms,
        analysis_ms,
        total_ms,
        result.parse_success,
        fallacy_count,
    )

    return DebateRespondResponse(
        response=result.response,
        thinking_style=result.thinking_style,
        next_focus=result.next_focus,
        tone=result.tone,
        persona_id=result.persona_id.value if hasattr(result.persona_id, "value") else str(result.persona_id),
        round_number=result.round_number,
        parse_success=result.parse_success,
        analysis=analysis_section,
    )
