"""Persona system prompts — one module per persona, versioned.

Each persona module exports: ROLE, STRATEGY, MISSION, BEHAVIOR, CONSTRAINTS, PROMPT_VERSION.
"""

from ai.enums import Persona

from ai.prompts.socrates import (
    ROLE as SOCRATES_ROLE,
    STRATEGY as SOCRATES_STRATEGY,
    MISSION as SOCRATES_MISSION,
    BEHAVIOR as SOCRATES_BEHAVIOR,
    CONSTRAINTS as SOCRATES_CONSTRAINTS,
    PROMPT_VERSION as SOCRATES_VERSION,
)
from ai.prompts.prosecutor import (
    ROLE as PROSECUTOR_ROLE,
    STRATEGY as PROSECUTOR_STRATEGY,
    MISSION as PROSECUTOR_MISSION,
    BEHAVIOR as PROSECUTOR_BEHAVIOR,
    CONSTRAINTS as PROSECUTOR_CONSTRAINTS,
    PROMPT_VERSION as PROSECUTOR_VERSION,
)
from ai.prompts.philosopher import (
    ROLE as PHILOSOPHER_ROLE,
    STRATEGY as PHILOSOPHER_STRATEGY,
    MISSION as PHILOSOPHER_MISSION,
    BEHAVIOR as PHILOSOPHER_BEHAVIOR,
    CONSTRAINTS as PHILOSOPHER_CONSTRAINTS,
    PROMPT_VERSION as PHILOSOPHER_VERSION,
)
from ai.prompts.devils_advocate import (
    ROLE as DEVILS_ADVOCATE_ROLE,
    STRATEGY as DEVILS_ADVOCATE_STRATEGY,
    MISSION as DEVILS_ADVOCATE_MISSION,
    BEHAVIOR as DEVILS_ADVOCATE_BEHAVIOR,
    CONSTRAINTS as DEVILS_ADVOCATE_CONSTRAINTS,
    PROMPT_VERSION as DEVILS_ADVOCATE_VERSION,
)


class PersonaSections:
    """Bundle of prompt sections for a single persona."""

    def __init__(
        self,
        role: str,
        strategy: str,
        mission: str,
        behavior: str,
        constraints: str,
        version: str,
    ) -> None:
        self.role = role
        self.strategy = strategy
        self.mission = mission
        self.behavior = behavior
        self.constraints = constraints
        self.version = version


PERSONA_SECTIONS: dict[Persona, PersonaSections] = {
    Persona.SOCRATES: PersonaSections(
        role=SOCRATES_ROLE,
        strategy=SOCRATES_STRATEGY,
        mission=SOCRATES_MISSION,
        behavior=SOCRATES_BEHAVIOR,
        constraints=SOCRATES_CONSTRAINTS,
        version=SOCRATES_VERSION,
    ),
    Persona.PROSECUTOR: PersonaSections(
        role=PROSECUTOR_ROLE,
        strategy=PROSECUTOR_STRATEGY,
        mission=PROSECUTOR_MISSION,
        behavior=PROSECUTOR_BEHAVIOR,
        constraints=PROSECUTOR_CONSTRAINTS,
        version=PROSECUTOR_VERSION,
    ),
    Persona.PHILOSOPHER: PersonaSections(
        role=PHILOSOPHER_ROLE,
        strategy=PHILOSOPHER_STRATEGY,
        mission=PHILOSOPHER_MISSION,
        behavior=PHILOSOPHER_BEHAVIOR,
        constraints=PHILOSOPHER_CONSTRAINTS,
        version=PHILOSOPHER_VERSION,
    ),
    Persona.DEVILS_ADVOCATE: PersonaSections(
        role=DEVILS_ADVOCATE_ROLE,
        strategy=DEVILS_ADVOCATE_STRATEGY,
        mission=DEVILS_ADVOCATE_MISSION,
        behavior=DEVILS_ADVOCATE_BEHAVIOR,
        constraints=DEVILS_ADVOCATE_CONSTRAINTS,
        version=DEVILS_ADVOCATE_VERSION,
    ),
}


def get_persona_sections(persona: Persona) -> PersonaSections:
    """Return the structured prompt sections for a persona."""
    return PERSONA_SECTIONS[persona]


def get_prompt(persona: Persona) -> tuple[str, str]:
    """Return (system_prompt, prompt_version) for backward compatibility."""
    s = PERSONA_SECTIONS[persona]
    combined = f"{s.role}\n\n{s.strategy}\n\n{s.mission}\n\n{s.behavior}\n\n{s.constraints}"
    return combined, s.version
