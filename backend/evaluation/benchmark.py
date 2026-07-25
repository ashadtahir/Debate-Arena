"""Benchmark dataset — loading and schema for evaluation samples."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ExpectedLabels:
    """Expected labels for a benchmark sample (for comparison, not enforcement)."""

    reasoning_level: str = ""
    likely_fallacies: list[str] = field(default_factory=list)
    evidence_strength: str = ""
    notes: str = ""


@dataclass(frozen=True)
class BenchmarkSample:
    """A single evaluation sample."""

    topic: str
    argument: str
    expected: ExpectedLabels


def load_dataset(path: str | Path | None = None) -> list[BenchmarkSample]:
    """Load the evaluation dataset from JSON.

    Defaults to datasets/debate_eval.json relative to this file's parent.
    """
    if path is None:
        path = Path(__file__).resolve().parent.parent / "datasets" / "debate_eval.json"
    else:
        path = Path(path)

    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    samples: list[BenchmarkSample] = []
    for item in raw:
        exp_raw = item.get("expected", {})
        expected = ExpectedLabels(
            reasoning_level=exp_raw.get("reasoning_level", ""),
            likely_fallacies=exp_raw.get("likely_fallacies", []),
            evidence_strength=exp_raw.get("evidence_strength", ""),
            notes=exp_raw.get("notes", ""),
        )
        samples.append(BenchmarkSample(
            topic=item["topic"],
            argument=item["argument"],
            expected=expected,
        ))

    return samples
