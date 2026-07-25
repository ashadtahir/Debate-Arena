"""Report comparison — computes deltas between two benchmark runs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MetricDelta:
    """A single metric comparison between two runs."""

    name: str
    current: float
    previous: float
    delta: float  # current - previous
    improved: bool
    significant: bool  # |delta| > threshold

    def arrow(self) -> str:
        if not self.significant:
            return "  ="
        return " ^" if self.improved else " v"

    def format_delta(self) -> str:
        if not self.significant:
            return f"{self.current:.1f} (unchanged)"
        sign = "+" if self.delta > 0 else ""
        return f"{self.previous:.1f} -> {self.current:.1f} ({sign}{self.delta:.1f})"


@dataclass
class ComparisonResult:
    """Full comparison between two benchmark runs."""

    current_timestamp: str
    previous_timestamp: str
    deltas: list[MetricDelta]
    improvement_count: int = 0
    regression_count: int = 0
    unchanged_count: int = 0


# Metrics where lower is better
LOWER_IS_BETTER = {"avg_latency_ms", "p50_latency_ms", "p95_latency_ms", "fallacy_detection_rate"}

# Threshold for "significant" change
THRESHOLD = 0.5


def compare_reports(current: dict, previous: dict) -> ComparisonResult:
    """Compare two metrics dicts and return deltas.

    Args:
        current: Metrics dict from the latest run (with 'metrics' key).
        previous: Metrics dict from the previous run (with 'metrics' key).
    """
    c = current.get("metrics", current)
    p = previous.get("metrics", previous)

    comparisons = [
        ("avg_overall_score", "Overall Score"),
        ("avg_logic_score", "Logic Score"),
        ("avg_evidence_score", "Evidence Score"),
        ("avg_coherence_score", "Coherence Score"),
        ("avg_persuasion_score", "Persuasion Score"),
        ("avg_latency_ms", "Avg Latency (ms)"),
        ("p50_latency_ms", "P50 Latency (ms)"),
        ("p95_latency_ms", "P95 Latency (ms)"),
        ("success_rate", "Success Rate"),
        ("fallacy_detection_rate", "Fallacy Detection Rate"),
        ("total_fallacies_detected", "Total Fallacies"),
    ]

    deltas: list[MetricDelta] = []
    improvements = 0
    regressions = 0
    unchanged = 0

    for key, label in comparisons:
        curr_val = float(c.get(key, 0))
        prev_val = float(p.get(key, 0))
        delta = curr_val - prev_val

        lower_better = key in LOWER_IS_BETTER
        improved = (delta < 0) if lower_better else (delta > 0)
        significant = abs(delta) >= THRESHOLD

        if significant:
            if improved:
                improvements += 1
            else:
                regressions += 1
        else:
            unchanged += 1

        deltas.append(MetricDelta(
            name=label,
            current=curr_val,
            previous=prev_val,
            delta=delta,
            improved=improved,
            significant=significant,
        ))

    return ComparisonResult(
        current_timestamp=current.get("timestamp", "unknown"),
        previous_timestamp=previous.get("timestamp", "unknown"),
        deltas=deltas,
        improvement_count=improvements,
        regression_count=regressions,
        unchanged_count=unchanged,
    )


def format_comparison_table(result: ComparisonResult) -> str:
    """Format a comparison result as a readable text table."""
    lines: list[str] = []

    lines.append("")
    lines.append(f"Comparison: {result.previous_timestamp} -> {result.current_timestamp}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"{'Metric':<26} {'Previous':>10} {'Current':>10} {'Delta':>12}")
    lines.append("-" * 60)

    for d in result.deltas:
        prev_str = f"{d.previous:.1f}"
        curr_str = f"{d.current:.1f}"
        delta_str = d.arrow() + " " + (f"{d.delta:+.1f}" if d.significant else "  =")
        lines.append(f"{d.name:<26} {prev_str:>10} {curr_str:>10} {delta_str:>12}")

    lines.append("-" * 60)
    lines.append(
        f"Improvements: {result.improvement_count}  |  "
        f"Regressions: {result.regression_count}  |  "
        f"Unchanged: {result.unchanged_count}"
    )
    lines.append("")

    return "\n".join(lines)
