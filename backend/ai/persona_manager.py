"""Persona-specific system prompts and debate behavior definitions."""

from __future__ import annotations

from dataclasses import dataclass

from ai.enums import Persona
from ai.prompts import get_prompt


@dataclass(frozen=True)
class PersonaConfig:
    id: Persona
    name: str
    system_prompt: str
    prompt_version: str
    debate_style: str


_PERSONA_META: dict[Persona, tuple[str, str]] = {
    Persona.SOCRATES: ("Socrates", "dialectic questioning"),
    Persona.PROSECUTOR: ("The Prosecutor", "evidence-based cross-examination"),
    Persona.PHILOSOPHER: ("The Philosopher", "first principles analysis"),
    Persona.DEVILS_ADVOCATE: ("Devil's Advocate", "adversarial counterpoint"),
}

PERSONA_CONFIGS: dict[Persona, PersonaConfig] = {}


def _build_configs() -> None:
    for persona, (name, style) in _PERSONA_META.items():
        prompt, version = get_prompt(persona)
        PERSONA_CONFIGS[persona] = PersonaConfig(
            id=persona,
            name=name,
            system_prompt=prompt,
            prompt_version=version,
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
