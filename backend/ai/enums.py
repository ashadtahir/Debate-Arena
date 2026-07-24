"""Strongly-typed enums for the debate domain."""

from __future__ import annotations

from enum import StrEnum


class Persona(StrEnum):
    SOCRATES = "socrates"
    PROSECUTOR = "prosecutor"
    PHILOSOPHER = "philosopher"
    DEVILS_ADVOCATE = "devils-advocate"


class Difficulty(StrEnum):
    APPRENTICE = "apprentice"
    SCHOLAR = "scholar"
    MASTER = "master"


class DebateSide(StrEnum):
    FOR = "for"
    AGAINST = "against"


class Tone(StrEnum):
    MEASURED = "measured"
    CHALLENGING = "challenging"
    PROVOCATIVE = "provocative"
    ANALYTICAL = "analytical"
    PHILOSOPHICAL = "philosophical"
    PROFESSIONAL = "professional"
