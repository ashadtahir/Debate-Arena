"""Feature extraction layer — independent signals extracted from argument text.

Embeddings from MiniLM are treated as semantic features (topic consistency,
reference retrieval, coherence heuristics) — NOT as direct reasoning scores.
Semantic similarity alone is a poor proxy for reasoning quality; these features
are combined with structural, reasoning, evidence, and language signals via
weighted scoring to produce the final ReasoningScore.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from analysis.clients.huggingface_client import cosine_similarity, encode

_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Reference embeddings — cached on first use for semantic feature retrieval
# ---------------------------------------------------------------------------

_LOGICAL_REFS = [
    "The argument follows a logical structure with premises leading to a conclusion.",
    "The reasoning uses connectives like because, therefore, and however to build a chain.",
]
_EVIDENCE_REFS = [
    "The argument cites specific data, studies, or research to support its claims.",
    "Concrete examples and statistics are used to back up the main points.",
]
_COUNTER_REFS = [
    "The argument acknowledges opposing viewpoints and addresses them directly.",
    "The argument considers what an opponent might say and responds proactively.",
]
_COHERENCE_REFS = [
    "The argument flows naturally from one point to the next with clear transitions.",
    "Each sentence builds on the previous one to construct a unified argument.",
]

_ref_cache: dict[str, object] = {}


def _get_ref_embeddings(key: str, refs: list[str]) -> object:
    if key not in _ref_cache:
        _ref_cache[key] = encode(refs, model=_MODEL)
    return _ref_cache[key]


# ---------------------------------------------------------------------------
# Feature dataclasses
# ---------------------------------------------------------------------------

@dataclass
class StructuralFeatures:
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    paragraph_count: int = 0

    @property
    def score(self) -> float:
        """0-1: structural adequacy. Penalizes very short or very dense arguments."""
        s = 0.0
        if self.word_count >= 20:
            s += 0.25
        if self.word_count >= 50:
            s += 0.1
        if self.sentence_count >= 2:
            s += 0.2
        if self.sentence_count >= 4:
            s += 0.1
        if 10 <= self.avg_sentence_length <= 30:
            s += 0.2
        if self.paragraph_count >= 2:
            s += 0.15
        return min(1.0, s)


@dataclass
class ReasoningFeatures:
    has_claim: bool = False
    has_premise: bool = False
    has_conclusion: bool = False
    connector_count: int = 0
    has_counterargument: bool = False

    @property
    def score(self) -> float:
        """0-1: reasoning structure quality."""
        s = 0.0
        if self.has_claim:
            s += 0.25
        if self.has_premise:
            s += 0.25
        if self.has_conclusion:
            s += 0.15
        s += min(0.2, self.connector_count * 0.05)
        if self.has_counterargument:
            s += 0.15
        return min(1.0, s)


@dataclass
class EvidenceFeatures:
    has_statistics: bool = False
    has_dates: bool = False
    has_examples: bool = False
    has_citations: bool = False
    has_numbers: bool = False
    named_entity_count: int = 0

    @property
    def score(self) -> float:
        """0-1: evidence richness."""
        s = 0.0
        if self.has_statistics:
            s += 0.3
        if self.has_dates:
            s += 0.1
        if self.has_examples:
            s += 0.2
        if self.has_citations:
            s += 0.2
        if self.has_numbers:
            s += 0.1
        if self.named_entity_count >= 1:
            s += 0.1
        return min(1.0, s)


@dataclass
class LanguageFeatures:
    hedging_count: int = 0
    certainty_count: int = 0
    repetition_score: float = 0.0
    vague_quantifier_count: int = 0
    absolute_language_count: int = 0

    @property
    def score(self) -> float:
        """0-1: language confidence and precision. Penalizes hedging, vagueness, repetition."""
        s = 0.8  # baseline
        s -= min(0.3, self.hedging_count * 0.1)
        s -= min(0.2, self.vague_quantifier_count * 0.05)
        s -= min(0.2, self.absolute_language_count * 0.1)
        s -= min(0.15, self.repetition_score * 0.15)
        s += min(0.2, self.certainty_count * 0.05)
        return max(0.0, min(1.0, s))


@dataclass
class SemanticFeatures:
    logical_similarity: float = 0.0
    evidence_similarity: float = 0.0
    counter_similarity: float = 0.0
    coherence_similarity: float = 0.0
    topic_consistency: float = 0.0

    @property
    def score(self) -> float:
        """0-1: aggregate semantic quality. No single similarity dominates."""
        return round(
            self.logical_similarity * 0.25
            + self.evidence_similarity * 0.2
            + self.coherence_similarity * 0.25
            + self.counter_similarity * 0.15
            + self.topic_consistency * 0.15,
            3,
        )


@dataclass
class ArgumentFeatures:
    structural: StructuralFeatures = field(default_factory=StructuralFeatures)
    reasoning: ReasoningFeatures = field(default_factory=ReasoningFeatures)
    evidence: EvidenceFeatures = field(default_factory=EvidenceFeatures)
    language: LanguageFeatures = field(default_factory=LanguageFeatures)
    semantic: SemanticFeatures = field(default_factory=SemanticFeatures)


# ---------------------------------------------------------------------------
# Feature extractors
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r"[.!?]+")
_CLAIM_MARKERS = {"assert", "claim", "argue", "believe", "maintain", "contend", "position", "stance"}
_PREMISE_MARKERS = {"because", "since", "given that", "as", "due to", "owing to", "for the reason"}
_CONCLUSION_MARKERS = {"therefore", "thus", "hence", "consequently", "so", "as a result", "accordingly"}
_COUNTER_MARKERS = {"however", "but", "although", "despite", "on the other hand", "nevertheless", "on the contrary", "concede"}
_CONNECTORS = {"because", "therefore", "however", "consequently", "since", "thus", "hence", "moreover", "furthermore", "additionally", "nevertheless", "nonetheless", "although", "whereas"}

_STAT_PATTERN = re.compile(r"\d+[\.\d]*\s*(%|percent|percentage|rate|ratio|proportion|times|fold)")
_DATE_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")
_EXAMPLE_MARKERS = {"for example", "for instance", "such as", "e.g.", "like", "including", "to illustrate"}
_CITATION_MARKERS = {"according to", "cited by", "published in", "study by", "research by", "report by", "found that"}
_NUMBER_PATTERN = re.compile(r"\b\d+[\.\d]*\b")
_NAMED_ENTITY_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b")

_HEDGING = {"i think", "i feel", "maybe", "probably", "sort of", "i guess", "it seems", "it appears", "might", "could", "possibly", "somewhat"}
_CERTAINTY = {"clearly", "undoubtedly", "certainly", "definitely", "must", "always", "never", "absolutely", "without doubt"}
_VAGUE_QUANTIFIERS = {"some", "many", "few", "several", "a lot", "most", "often", "sometimes", "usually", "generally"}
_ABSOLUTES = {"all", "none", "every", "always", "never", "everyone", "nobody", "everything", "nothing", "no one", "everybody"}


def extract_structural(text: str) -> StructuralFeatures:
    words = text.split()
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    return StructuralFeatures(
        word_count=len(words),
        sentence_count=len(sentences),
        avg_sentence_length=round(avg_len, 1),
        paragraph_count=max(len(paragraphs), 1),
    )


def extract_reasoning(text: str) -> ReasoningFeatures:
    lower = text.lower()
    connector_count = sum(1 for c in _CONNECTORS if c in lower)
    return ReasoningFeatures(
        has_claim=any(m in lower for m in _CLAIM_MARKERS),
        has_premise=any(m in lower for m in _PREMISE_MARKERS),
        has_conclusion=any(m in lower for m in _CONCLUSION_MARKERS),
        connector_count=connector_count,
        has_counterargument=any(m in lower for m in _COUNTER_MARKERS),
    )


def extract_evidence(text: str) -> EvidenceFeatures:
    lower = text.lower()
    return EvidenceFeatures(
        has_statistics=bool(_STAT_PATTERN.search(text)),
        has_dates=bool(_DATE_PATTERN.search(text)),
        has_examples=any(m in lower for m in _EXAMPLE_MARKERS),
        has_citations=any(m in lower for m in _CITATION_MARKERS),
        has_numbers=bool(_NUMBER_PATTERN.search(text)),
        named_entity_count=len(_NAMED_ENTITY_PATTERN.findall(text)),
    )


def extract_language(text: str) -> LanguageFeatures:
    lower = text.lower()
    words = lower.split()
    unique_words = set(words)
    repetition = 1.0 - (len(unique_words) / max(len(words), 1))
    return LanguageFeatures(
        hedging_count=sum(1 for m in _HEDGING if m in lower),
        certainty_count=sum(1 for m in _CERTAINTY if m in lower),
        repetition_score=round(repetition, 2),
        vague_quantifier_count=sum(1 for m in _VAGUE_QUANTIFIERS if f" {m} " in f" {lower} "),
        absolute_language_count=sum(1 for m in _ABSOLUTES if f" {m} " in f" {lower} "),
    )


def extract_semantic(text: str) -> SemanticFeatures:
    """Compute semantic features via MiniLM embeddings.

    These are NOT direct reasoning scores. Embedding similarity measures topical
    overlap with well-reasoned reference statements — one signal among many.
    A high similarity to a logical reference does not mean the argument is logical;
    it means the argument discusses similar content. The SemanticReasoningAnalyzer
    combines this with structural, reasoning, evidence, and language features
    to produce a more robust score.
    """
    all_refs = _LOGICAL_REFS + _EVIDENCE_REFS + _COUNTER_REFS + _COHERENCE_REFS
    texts = [text] + all_refs
    embeddings = encode(texts, model=_MODEL)

    arg_emb = embeddings[0]
    idx = 1

    logical_sims = [cosine_similarity(arg_emb, embeddings[idx + i]) for i in range(len(_LOGICAL_REFS))]
    idx += len(_LOGICAL_REFS)

    evidence_sims = [cosine_similarity(arg_emb, embeddings[idx + i]) for i in range(len(_EVIDENCE_REFS))]
    idx += len(_EVIDENCE_REFS)

    counter_sims = [cosine_similarity(arg_emb, embeddings[idx + i]) for i in range(len(_COUNTER_REFS))]
    idx += len(_COUNTER_REFS)

    coherence_sims = [cosine_similarity(arg_emb, embeddings[idx + i]) for i in range(len(_COHERENCE_REFS))]

    topic_consistency = round(
        (max(logical_sims) + max(evidence_sims) + max(counter_sims) + max(coherence_sims)) / 4,
        3,
    )

    return SemanticFeatures(
        logical_similarity=round(max(logical_sims), 3),
        evidence_similarity=round(max(evidence_sims), 3),
        counter_similarity=round(max(counter_sims), 3),
        coherence_similarity=round(max(coherence_sims), 3),
        topic_consistency=topic_consistency,
    )


def extract_all(text: str) -> ArgumentFeatures:
    return ArgumentFeatures(
        structural=extract_structural(text),
        reasoning=extract_reasoning(text),
        evidence=extract_evidence(text),
        language=extract_language(text),
        semantic=extract_semantic(text),
    )
