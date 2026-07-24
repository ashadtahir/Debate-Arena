"""Heuristic fallacy detection — multi-signal scoring per fallacy type.

Each function receives the raw text plus pre-extracted features and returns a
confidence score (0-1) plus evidence text.  No single signal dominates;
structural, language, reasoning, and semantic signals are combined.
"""

from __future__ import annotations

import re

from analysis.features import ArgumentFeatures
from analysis.fallacies.schemas import Fallacy

_ABSOLUTES = {"all", "none", "every", "always", "never", "everyone", "nobody", "everything", "nothing", "no one", "everybody"}
_VAGUE_QUANTIFIERS = {"some", "many", "few", "several", "a lot", "most", "often", "sometimes", "usually", "generally"}

_EITHER_OR = re.compile(r"\b(?:either\s+.+?\s+or\b|it'?s?\s+(?:either|one)\s+)", re.I)
_DISMISSIVE_PRONOUNS = re.compile(r"\b(?:you(?:'re| are)\s+(?:saying|suggesting|claiming|wanting|arguing))\b", re.I)
_SLOPE_CONNECTORS = re.compile(r"\b(?:will (?:inevitably|certainly|definitely)|lead to|result in|end up|before you know it)\b", re.I)
_AUTHORITY_MARKERS = re.compile(r"\b(?:according to|cited by|study by|research by|told us|stated that)\b", re.I)
_AUTHORITY_NAMED = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|states|claims|argued|believes|told)\b")
_CIRCULAR_PATTERNS = re.compile(r"\b(bad|good|wrong|right|true|false|works|effective)\b.*?\b(because|since|as)\b.*?\b\1\b", re.I)

_SLOPE_EXTRAPOLATION = re.compile(r"\b(?:if .+?,?\s*(?:then\s+)?(?:soon|eventually|before long|in no time|it'?s? only a matter of time))\b", re.I)
_SLOPE_CHAIN = re.compile(r"\b(?:then\s+\w+.*?,?\s*(?:then|and then|which leads to|which results in))\b", re.I)


def _find_span(text: str, needle: str) -> tuple[int, int] | None:
    idx = text.lower().find(needle.lower())
    if idx == -1:
        return None
    return idx, idx + len(needle)


def _confidence(*signals: float) -> float:
    """Combine multiple 0-1 signals into a single confidence via weighted blend.

    Uses max * 0.4 + avg * 0.6 — the strongest signal anchors the result while
    weaker signals pull it toward the average.  This avoids both false positives
    (one weak signal shouldn't drag down a strong pattern) and overconfidence
    (a single strong signal shouldn't dominate entirely).
    """
    valid = [max(0.0, min(1.0, s)) for s in signals if s > 0]
    if not valid:
        return 0.0
    return round(max(valid) * 0.4 + (sum(valid) / len(valid)) * 0.6, 2)


def detect_hasty_generalization(text: str, features: ArgumentFeatures) -> Fallacy | None:
    lower = text.lower()
    found_absolutes = [w for w in _ABSOLUTES if f" {w} " in f" {lower} "]
    found_vague = [w for w in _VAGUE_QUANTIFIERS if f" {w} " in f" {lower} "]

    count_signal = (len(found_absolutes) + len(found_vague)) / 6
    length_signal = 1.0 - min(1.0, features.structural.word_count / 40)
    evidence_signal = 1.0 - features.evidence.score

    conf = _confidence(count_signal, length_signal, evidence_signal)
    if conf < 0.3:
        return None

    words = " ".join(found_absolutes[:2] + found_vague[:2])
    span = _find_span(text, words) if words else None
    return Fallacy(
        type="hasty_generalization",
        name="Hasty Generalization",
        confidence=conf,
        explanation=f"Uses broad quantifiers ({words or 'general terms'}) without sufficient evidence to support a universal claim.",
        evidence=_extract_evidence_snippet(text, found_absolutes + found_vague),
        span_start=span[0] if span else None,
        span_end=span[1] if span else None,
    )


def detect_false_dilemma(text: str, features: ArgumentFeatures) -> Fallacy | None:
    lower = text.lower()
    either_or = bool(_EITHER_OR.search(lower))
    if not either_or:
        return None

    connector_signal = 0.65
    counter_signal = 0.0 if features.reasoning.has_counterargument else 0.25
    certainty_signal = min(0.35, features.language.absolute_language_count * 0.15)

    conf = _confidence(connector_signal, counter_signal, certainty_signal)
    if conf < 0.3:
        return None

    match = _EITHER_OR.search(text)
    evidence_text = text[match.start():match.end() + 30] if match else text[:60]
    return Fallacy(
        type="false_dilemma",
        name="False Dilemma",
        confidence=conf,
        explanation="Presents only two options when more alternatives likely exist.",
        evidence=evidence_text.strip(),
        span_start=match.start() if match else None,
        span_end=min(match.end() + 30, len(text)) if match else None,
    )


def detect_straw_man(text: str, features: ArgumentFeatures) -> Fallacy | None:
    match = _DISMISSIVE_PRONOUNS.search(text)
    if not match:
        return None

    confidence = 0.55
    evidence_text = text[match.start():min(match.end() + 20, len(text))]
    return Fallacy(
        type="straw_man",
        name="Straw Man",
        confidence=confidence,
        explanation="Appears to misrepresent an opponent's position by restating it in a distorted form.",
        evidence=evidence_text.strip(),
        span_start=match.start(),
        span_end=min(match.end() + 20, len(text)),
    )


def detect_appeal_to_authority(text: str, features: ArgumentFeatures) -> Fallacy | None:
    lower = text.lower()
    has_authority = bool(_AUTHORITY_MARKERS.search(lower))
    has_named_authority = bool(_AUTHORITY_NAMED.search(text))
    has_evidence = features.evidence.has_statistics or features.evidence.has_citations

    if not has_authority and not has_named_authority:
        return None

    conf = 0.4 if has_evidence else 0.55
    if not features.evidence.has_statistics:
        conf += 0.1
    if has_named_authority:
        conf += 0.1

    match = _AUTHORITY_MARKERS.search(text) or _AUTHORITY_NAMED.search(text)
    evidence_text = text[match.start():min(match.end() + 40, len(text))] if match else text[:60]
    return Fallacy(
        type="appeal_to_authority",
        name="Appeal to Authority",
        confidence=round(min(0.9, conf), 2),
        explanation="Relies on an authority figure's statement rather than independent evidence.",
        evidence=evidence_text.strip(),
        span_start=match.start() if match else None,
        span_end=min(match.end() + 40, len(text)) if match else None,
    )


def detect_slippery_slope(text: str, features: ArgumentFeatures) -> Fallacy | None:
    lower = text.lower()
    has_slope_connector = bool(_SLOPE_CONNECTORS.search(lower))
    has_extrapolation = bool(_SLOPE_EXTRAPOLATION.search(lower))
    has_chain = bool(_SLOPE_CHAIN.search(lower))

    # Require at least one actual slope signal — absence of counterarguments alone is not enough
    connector_signal = 0.0
    if has_slope_connector:
        connector_signal = 0.6
    elif has_extrapolation:
        connector_signal = 0.5
    elif has_chain:
        connector_signal = 0.45

    if connector_signal == 0.0:
        return None

    # Escalation language strengthens the signal
    escalation_signal = 0.0
    if "eventually" in lower or "inevitably" in lower:
        escalation_signal += 0.3
    if "all" in lower or "everything" in lower or "every" in lower:
        escalation_signal += 0.2
    escalation_signal = min(0.5, escalation_signal)

    conf = _confidence(connector_signal, escalation_signal) if escalation_signal > 0 else connector_signal * 0.6
    if conf < 0.3:
        return None

    match = _SLOPE_CONNECTORS.search(text) or _SLOPE_EXTRAPOLATION.search(text) or _SLOPE_CHAIN.search(text)
    evidence_text = text[match.start():min(match.end() + 20, len(text))] if match else text[:60]
    return Fallacy(
        type="slippery_slope",
        name="Slippery Slope",
        confidence=conf,
        explanation="Assumes a chain of events will inevitably lead to extreme consequences without justification.",
        evidence=evidence_text.strip(),
        span_start=match.start() if match else None,
        span_end=min(match.end() + 20, len(text)) if match else None,
    )


def detect_circular_reasoning(text: str, features: ArgumentFeatures) -> Fallacy | None:
    match = _CIRCULAR_PATTERNS.search(text)
    if not match:
        return None

    confidence = 0.5
    evidence_text = text[match.start():min(match.end() + 10, len(text))]
    return Fallacy(
        type="circular_reasoning",
        name="Circular Reasoning",
        confidence=confidence,
        explanation="The argument assumes its conclusion as a premise — it restates the claim instead of supporting it.",
        evidence=evidence_text.strip(),
        span_start=match.start(),
        span_end=min(match.end() + 10, len(text)),
    )


def _extract_evidence_snippet(text: str, keywords: list[str]) -> str:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            start = max(0, idx - 15)
            end = min(len(text), idx + len(kw) + 15)
            return text[start:end].strip()
    return text[:60]


ALL_DETECTORS = [
    detect_hasty_generalization,
    detect_false_dilemma,
    detect_straw_man,
    detect_appeal_to_authority,
    detect_slippery_slope,
    detect_circular_reasoning,
]
