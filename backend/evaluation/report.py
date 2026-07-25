"""Report generator — produces Markdown benchmark reports."""

from __future__ import annotations

from datetime import datetime, timezone

from ai.prompts.base import PROMPT_VERSION
from ai.memory import MEMORY_VERSION

ANALYSIS_VERSION = "1.0"


def generate_report(
    results: list[dict],
    metrics: object,
    *,
    run_timestamp: str | None = None,
) -> str:
    """Generate a Markdown benchmark report from results and metrics.

    Args:
        results: List of per-sample result dicts from runner.
        metrics: BenchmarkMetrics instance from metrics.compute_metrics.
        run_timestamp: ISO timestamp string. Defaults to now (UTC).
    """
    ts = run_timestamp or datetime.now(timezone.utc).isoformat()

    lines: list[str] = []

    lines.append("# DebateArena Benchmark Report")
    lines.append("")
    lines.append(f"**Generated:** {ts}")
    lines.append(f"**Prompt Version:** {PROMPT_VERSION}")
    lines.append(f"**Memory Version:** {MEMORY_VERSION}")
    lines.append(f"**Analysis Version:** {ANALYSIS_VERSION}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Dataset Size | {metrics.dataset_size} |")
    lines.append(f"| Success Rate | {metrics.success_rate:.1%} |")
    lines.append(f"| Successes | {metrics.success_count} |")
    lines.append(f"| Failures | {metrics.failure_count} |")
    lines.append("")

    # Latency
    lines.append("## Latency")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Average | {metrics.avg_latency_ms:.0f}ms |")
    lines.append(f"| P50 | {metrics.p50_latency_ms:.0f}ms |")
    lines.append(f"| P95 | {metrics.p95_latency_ms:.0f}ms |")
    lines.append("")

    # Reasoning Scores
    lines.append("## Reasoning Scores")
    lines.append("")
    lines.append(f"| Dimension | Average (0-100) |")
    lines.append(f"|-----------|-----------------|")
    lines.append(f"| Overall | {metrics.avg_overall_score:.1f} |")
    lines.append(f"| Logic | {metrics.avg_logic_score:.1f} |")
    lines.append(f"| Evidence | {metrics.avg_evidence_score:.1f} |")
    lines.append(f"| Coherence | {metrics.avg_coherence_score:.1f} |")
    lines.append(f"| Persuasion | {metrics.avg_persuasion_score:.1f} |")
    lines.append("")

    # Score Distribution
    lines.append("## Score Distribution")
    lines.append("")
    lines.append(f"| Dimension | Very Low | Low | Medium | High | Very High |")
    lines.append(f"|-----------|----------|-----|--------|------|-----------|")
    for dim in ["overall", "logic", "evidence", "coherence", "persuasion"]:
        row = [dim.capitalize()]
        for bucket in ["very_low", "low", "medium", "high", "very_high"]:
            key = f"{dim}_{bucket}"
            count = metrics.score_distribution.get(key, 0)
            row.append(str(count))
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # Fallacy Detection
    lines.append("## Fallacy Detection")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Detected | {metrics.total_fallacies_detected} |")
    lines.append(f"| Detection Rate | {metrics.fallacy_detection_rate:.2f} per argument |")
    lines.append("")
    if metrics.fallacy_type_counts:
        lines.append("### By Type")
        lines.append("")
        lines.append(f"| Fallacy Type | Count |")
        lines.append(f"|-------------|-------|")
        for ftype, count in sorted(metrics.fallacy_type_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {ftype} | {count} |")
        lines.append("")

    # Per-sample results (compact)
    lines.append("## Sample Results")
    lines.append("")
    lines.append(f"| # | Topic | Success | Score | Latency | Fallacies |")
    lines.append(f"|---|-------|---------|-------|---------|-----------|")
    for i, r in enumerate(results, start=1):
        topic = r.get("topic", "")[:40]
        success = "Yes" if r.get("success") else "No"
        score = f"{r['scores']['overall'] * 100:.0f}" if r.get("scores") else "N/A"
        latency = f"{r.get('latency_ms', 0)}ms"
        fallacies = str(len(r.get("fallacies", [])))
        lines.append(f"| {i} | {topic} | {success} | {score} | {latency} | {fallacies} |")
    lines.append("")

    return "\n".join(lines)
