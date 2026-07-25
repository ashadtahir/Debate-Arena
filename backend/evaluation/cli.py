"""Benchmark CLI — run, save, compare, and report.

Usage:
    python -m evaluation.cli                     # Run benchmark, save report, compare
    python -m evaluation.cli --dataset path.json # Custom dataset
    python -m evaluation.cli --reports-dir path  # Custom reports directory

Reports are saved to backend/reports/ by default.
Each run creates two files:
    - report_YYYYMMDD_HHMMSS.md   (Markdown report)
    - metrics_YYYYMMDD_HHMMSS.json (machine-readable metrics)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from evaluation.compare import compare_reports, format_comparison_table
from evaluation.metrics import compute_metrics
from evaluation.report import generate_report
from evaluation.runner import run_benchmark


def _reports_dir(base: Path) -> Path:
    d = base / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _find_previous_report(dirpath: Path, current_name: str) -> Path | None:
    """Find the most recent metrics JSON that isn't the current one."""
    jsons = sorted(dirpath.glob("metrics_*.json"), reverse=True)
    for j in jsons:
        if j.name != current_name:
            return j
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="DebateArena Benchmark CLI")
    parser.add_argument("--dataset", default=None, help="Path to evaluation dataset JSON")
    parser.add_argument("--reports-dir", default=None, help="Directory for reports")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    reports = _reports_dir(Path(args.reports_dir) if args.reports_dir else base)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # --- Run benchmark ---
    print("Running benchmark...")
    start = time.monotonic()
    results = asyncio.run(run_benchmark(args.dataset))
    run_ms = round((time.monotonic() - start) * 1000)
    print(f"Benchmark complete: {len(results)} samples in {run_ms}ms")

    # --- Compute metrics ---
    metrics = compute_metrics(results)

    # --- Save metrics JSON ---
    metrics_data = {
        "timestamp": ts,
        "run_ms": run_ms,
        "metrics": metrics.to_dict(),
    }
    metrics_name = f"metrics_{ts}.json"
    metrics_path = reports / metrics_name
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Metrics saved: {metrics_path}")

    # --- Generate and save report ---
    report_md = generate_report(results, metrics, run_timestamp=ts)
    report_name = f"report_{ts}.md"
    report_path = reports / report_name
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Report saved: {report_path}")

    # --- Compare with previous ---
    prev_path = _find_previous_report(reports, metrics_name)
    if prev_path:
        with open(prev_path, encoding="utf-8") as f:
            prev_data = json.load(f)
        comparison = compare_reports(metrics_data, prev_data)
        print(format_comparison_table(comparison))
    else:
        print("\nNo previous benchmark found — skipping comparison.")
        print(f"First run summary:")
        print(f"  Dataset size:   {metrics.dataset_size}")
        print(f"  Success rate:   {metrics.success_rate:.1%}")
        print(f"  Avg score:      {metrics.avg_overall_score:.1f}")
        print(f"  Avg latency:    {metrics.avg_latency_ms:.0f}ms")
        print(f"  Fallacies:      {metrics.total_fallacies_detected}")
        print()


if __name__ == "__main__":
    main()
