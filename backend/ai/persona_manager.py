"""Persona-specific system prompts and debate behavior definitions."""

from __future__ import annotations

from dataclasses import dataclass

from ai.enums import Persona
from ai.prompts import PersonaSections, get_persona_sections


@dataclass(frozen=True)
class PromptSections:
    """Structured prompt sections for a persona."""

    role: str
    strategy: str
    mission: str
    behavior: str
    constraints: str


@dataclass(frozen=True)
class PersonaConfig:
    """Complete persona configuration with structured prompt sections."""

    id: Persona
    name: str
    sections: PromptSections
    prompt_version: str
    debate_style: str


def _sections_to_prompt_sections(s: PersonaSections) -> PromptSections:
    return PromptSections(
        role=s.role,
        strategy=s.strategy,
        mission=s.mission,
        behavior=s.behavior,
        constraints=s.constraints,
    )


_PERSONA_META: dict[Persona, tuple[str, str]] = {
    Persona.SOCRATES: ("Socrates", "dialectic questioning"),
    Persona.PROSECUTOR: ("The Prosecutor", "evidence-based cross-examination"),
    Persona.PHILOSOPHER: ("The Philosopher", "first principles analysis"),
    Persona.DEVILS_ADVOCATE: ("Devil's Advocate", "adversarial counterpoint"),
}

PERSONA_CONFIGS: dict[Persona, PersonaConfig] = {}


def _build_configs() -> None:
    for persona, (name, style) in _PERSONA_META.items():
        sections = get_persona_sections(persona)
        PERSONA_CONFIGS[persona] = PersonaConfig(
            id=persona,
            name=name,
            sections=_sections_to_prompt_sections(sections),
            prompt_version=sections.version,
            debate_style=style,
        )


_build_configs()


def get_persona_config(persona_id: Persona) -> PersonaConfig:
    """Look up persona config by enum. Raises ValueError if not found."""
    config = PERSONA_CONFIGS.get(persona_id)
    if not config:
        available = ", ".join(p.value for p in PERSONA_CONFIGS)
        raise ValueError(f"Unknown persona '{persona_id}'. Available: {available}")
    return config
