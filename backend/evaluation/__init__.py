"""Evaluation framework — isolated benchmarking for the AnalysisEngine.

This package is completely isolated from production code. Nothing in the
main application depends on evaluation modules.

Usage:
    python -m evaluation.cli                     # Run benchmark, save report, compare
    python -m evaluation.cli --dataset path.json # Custom dataset
    python -m evaluation.cli --reports-dir path   # Custom reports directory
"""
