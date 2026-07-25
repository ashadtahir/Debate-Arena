"""Evaluation metrics — pure functions for benchmark measurement.

All functions take lists of results and return numeric metrics.
Add new metrics by writing a function that accepts the results list.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class BenchmarkMetrics:
    """Aggregate metrics from a benchmark run."""

    dataset_size: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0

    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0

    avg_overall_score: float = 0.0
    avg_logic_score: float = 0.0
    avg_evidence_score: float = 0.0
    avg_coherence_score: float = 0.0
    avg_persuasion_score: float = 0.0

    fallacy_detection_rate: float = 0.0
    total_fallacies_detected: int = 0
    fallacy_type_counts: dict[str, int] = field(default_factory=dict)

    # Score distribution buckets (0-100 scale)
    score_distribution: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "dataset_size": self.dataset_size,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "p50_latency_ms": self.p50_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "avg_overall_score": self.avg_overall_score,
            "avg_logic_score": self.avg_logic_score,
            "avg_evidence_score": self.avg_evidence_score,
            "avg_coherence_score": self.avg_coherence_score,
            "avg_persuasion_score": self.avg_persuasion_score,
            "fallacy_detection_rate": self.fallacy_detection_rate,
            "total_fallacies_detected": self.total_fallacies_detected,
            "fallacy_type_counts": self.fallacy_type_counts,
            "score_distribution": self.score_distribution,
        }

    @classmethod
    def from_dict(cls, d: dict) -> BenchmarkMetrics:
        """Deserialize from a dict."""
        return cls(
            dataset_size=d.get("dataset_size", 0),
            success_count=d.get("success_count", 0),
            failure_count=d.get("failure_count", 0),
            success_rate=d.get("success_rate", 0.0),
            avg_latency_ms=d.get("avg_latency_ms", 0.0),
            p50_latency_ms=d.get("p50_latency_ms", 0.0),
            p95_latency_ms=d.get("p95_latency_ms", 0.0),
            avg_overall_score=d.get("avg_overall_score", 0.0),
            avg_logic_score=d.get("avg_logic_score", 0.0),
            avg_evidence_score=d.get("avg_evidence_score", 0.0),
            avg_coherence_score=d.get("avg_coherence_score", 0.0),
            avg_persuasion_score=d.get("avg_persuasion_score", 0.0),
            fallacy_detection_rate=d.get("fallacy_detection_rate", 0.0),
            total_fallacies_detected=d.get("total_fallacies_detected", 0),
            fallacy_type_counts=d.get("fallacy_type_counts", {}),
            score_distribution=d.get("score_distribution", {}),
        )


def compute_metrics(results: list[dict]) -> BenchmarkMetrics:
    """Compute aggregate metrics from a list of benchmark results.

    Each result dict is expected to have:
        - success: bool
        - latency_ms: float
        - scores: dict (overall, logic, evidence, coherence, persuasion)
        - fallacies: list[dict]
    """
    m = BenchmarkMetrics()
    m.dataset_size = len(results)

    if not results:
        return m

    successes = [r for r in results if r.get("success", False)]
    failures = [r for r in results if not r.get("success", False)]

    m.success_count = len(successes)
    m.failure_count = len(failures)
    m.success_rate = round(len(successes) / len(results), 4)

    # Latency
    latencies = [r["latency_ms"] for r in results if "latency_ms" in r]
    if latencies:
        m.avg_latency_ms = round(statistics.mean(latencies), 1)
        sorted_lat = sorted(latencies)
        m.p50_latency_ms = round(statistics.median(sorted_lat), 1)
        p95_idx = int(len(sorted_lat) * 0.95)
        m.p95_latency_ms = round(sorted_lat[min(p95_idx, len(sorted_lat) - 1)], 1)

    # Scores (only from successful results)
    all_scores: dict[str, list[float]] = {
        "overall": [],
        "logic": [],
        "evidence": [],
        "coherence": [],
        "persuasion": [],
    }

    for r in successes:
        scores = r.get("scores", {})
        for key in all_scores:
            if key in scores:
                all_scores[key].append(scores[key] * 100)  # Convert 0-1 to 0-100

    if all_scores["overall"]:
        m.avg_overall_score = round(statistics.mean(all_scores["overall"]), 1)
        m.avg_logic_score = round(statistics.mean(all_scores["logic"]), 1)
        m.avg_evidence_score = round(statistics.mean(all_scores["evidence"]), 1)
        m.avg_coherence_score = round(statistics.mean(all_scores["coherence"]), 1)
        m.avg_persuasion_score = round(statistics.mean(all_scores["persuasion"]), 1)

    # Score distribution buckets
    for key in ["overall", "logic", "evidence", "coherence", "persuasion"]:
        for score in all_scores[key]:
            bucket = _score_bucket(score)
            dist_key = f"{key}_{bucket}"
            m.score_distribution[dist_key] = m.score_distribution.get(dist_key, 0) + 1

    # Fallacy detection
    total_fallacies = 0
    type_counts: dict[str, int] = {}
    for r in successes:
        fallacies = r.get("fallacies", [])
        total_fallacies += len(fallacies)
        for f in fallacies:
            ftype = f.get("type", "unknown")
            type_counts[ftype] = type_counts.get(ftype, 0) + 1

    m.total_fallacies_detected = total_fallacies
    m.fallacy_type_counts = type_counts
    if successes:
        m.fallacy_detection_rate = round(total_fallacies / len(successes), 2)

    return m


def _score_bucket(score: float) -> str:
    """Map a 0-100 score to a named bucket."""
    if score < 20:
        return "very_low"
    elif score < 40:
        return "low"
    elif score < 60:
        return "medium"
    elif score < 80:
        return "high"
    else:
        return "very_high"
