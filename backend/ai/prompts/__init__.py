"""Persona system prompts — one module per persona, versioned."""

from ai.enums import Persona

from ai.prompts.socrates import SYSTEM_PROMPT as SOCRATES_PROMPT, PROMPT_VERSION as SOCRATES_VERSION
from ai.prompts.prosecutor import SYSTEM_PROMPT as PROSECUTOR_PROMPT, PROMPT_VERSION as PROSECUTOR_VERSION
from ai.prompts.philosopher import SYSTEM_PROMPT as PHILOSOPHER_PROMPT, PROMPT_VERSION as PHILOSOPHER_VERSION
from ai.prompts.devils_advocate import SYSTEM_PROMPT as DEVILS_ADVOCATE_PROMPT, PROMPT_VERSION as DEVILS_ADVOCATE_VERSION

PROMPT_MAP: dict[Persona, tuple[str, str]] = {
    Persona.SOCRATES: (SOCRATES_PROMPT, SOCRATES_VERSION),
    Persona.PROSECUTOR: (PROSECUTOR_PROMPT, PROSECUTOR_VERSION),
    Persona.PHILOSOPHER: (PHILOSOPHER_PROMPT, PHILOSOPHER_VERSION),
    Persona.DEVILS_ADVOCATE: (DEVILS_ADVOCATE_PROMPT, DEVILS_ADVOCATE_VERSION),
}


def get_prompt(persona: Persona) -> tuple[str, str]:
    """Return (system_prompt, prompt_version) for a persona."""
    return PROMPT_MAP[persona]
