"""Response parser — extracts structured debate data from LLM text output.

Uses a 3-level fallback strategy:
1. Parse LLM response as JSON directly
2. Extract JSON from markdown code fences (```json ... ```)
3. Fall back to raw text extraction with default values

Never raises — malformed output always returns a safe default with
parse_success=False so the debate can continue gracefully.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass
class ParsedResponse:
    response: str
    thinking_style: str
    next_focus: str
    tone: str
    raw: str
    parse_success: bool


def parse_llm_response(raw: str) -> ParsedResponse:
    """Parse the LLM's JSON response into structured fields.

    Falls back to extracting the 'response' field if the full JSON is malformed.
    Returns a raw text fallback if nothing parses.
    """
    raw_stripped = raw.strip()

    # Try direct JSON parse
    parsed = _try_parse_json(raw_stripped)
    if parsed:
        return _from_dict(parsed, raw, parse_success=True)

    # Try extracting JSON from markdown code blocks
    code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw_stripped, re.DOTALL)
    if code_block:
        parsed = _try_parse_json(code_block.group(1).strip())
        if parsed:
            return _from_dict(parsed, raw, parse_success=True)

    # Try finding JSON object in the text
    json_match = re.search(r"\{.*\}", raw_stripped, re.DOTALL)
    if json_match:
        parsed = _try_parse_json(json_match.group(0))
        if parsed:
            return _from_dict(parsed, raw, parse_success=True)

    # Last resort: use the raw text as the response
    return ParsedResponse(
        response=raw_stripped or "I need to think about that. Could you restate your position?",
        thinking_style="unparsed response",
        next_focus="continue the debate",
        tone="neutral",
        raw=raw,
        parse_success=False,
    )


def _try_parse_json(text: str) -> dict | None:
    """Attempt to parse text as JSON. Returns None on failure."""
    try:
        result = json.loads(text)
        return result if isinstance(result, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def _from_dict(data: dict, raw: str, *, parse_success: bool) -> ParsedResponse:
    """Extract fields from a parsed dict with defaults."""
    return ParsedResponse(
        response=data.get("response", "I appreciate that point. Let me consider it."),
        thinking_style=data.get("thinking_style", "analytical"),
        next_focus=data.get("next_focus", "continue the argument"),
        tone=data.get("tone", "measured"),
        raw=raw,
        parse_success=parse_success,
    )
