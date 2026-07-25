"""Benchmark runner — executes the evaluation dataset against AnalysisEngine."""

from __future__ import annotations

import asyncio
import logging
import time

from analysis.analysis_engine import AnalysisEngine
from evaluation.benchmark import BenchmarkSample, load_dataset

logger = logging.getLogger(__name__)


async def run_benchmark(
    dataset_path: str | None = None,
    *,
    engine: AnalysisEngine | None = None,
) -> list[dict]:
    """Run the full benchmark dataset through the AnalysisEngine.

    Returns a list of result dicts, one per sample. Each dict contains:
        - topic, argument, expected (from dataset)
        - success: bool
        - latency_ms: float
        - scores: dict (overall, logic, evidence, coherence, persuasion)
        - fallacies: list[dict]
        - observations: list[dict]
        - insight: str
        - error: str (if failed)
    """
    engine = engine or AnalysisEngine()
    samples = load_dataset(dataset_path)

    results: list[dict] = []
    total = len(samples)

    for idx, sample in enumerate(samples, start=1):
        logger.info("Running sample %d/%d: %s", idx, total, sample.topic[:50])
        result = await _run_sample(sample, engine)
        results.append(result)

    logger.info("Benchmark complete: %d samples processed", total)
    return results


async def _run_sample(sample: BenchmarkSample, engine: AnalysisEngine) -> dict:
    """Run a single benchmark sample through the AnalysisEngine."""
    start = time.monotonic()
    try:
        result = await engine.analyze(
            sample.argument,
            persona="socrates",
            difficulty="scholar",
            round_number=1,
        )
        latency_ms = round((time.monotonic() - start) * 1000)

        return {
            "topic": sample.topic,
            "argument": sample.argument[:100],
            "expected": {
                "reasoning_level": sample.expected.reasoning_level,
                "evidence_strength": sample.expected.evidence_strength,
                "likely_fallacies": sample.expected.likely_fallacies,
            },
            "success": True,
            "latency_ms": latency_ms,
            "scores": {
                "overall": result.scores.overall,
                "logic": result.scores.logical_validity,
                "evidence": result.scores.evidence_use,
                "coherence": result.scores.coherence,
                "persuasion": result.scores.counterargument_readiness,
            },
            "fallacies": [
                {
                    "type": f.type.value if hasattr(f.type, "value") else str(f.type),
                    "name": f.name,
                    "confidence": round(f.confidence, 2),
                }
                for f in result.fallacies
            ],
            "observations": [
                {
                    "category": o.category.value,
                    "severity": o.severity.value,
                }
                for o in result.observations
            ],
            "insight": result.insight,
        }

    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000)
        logger.exception("Sample failed: %s", sample.topic[:50])
        return {
            "topic": sample.topic,
            "argument": sample.argument[:100],
            "expected": {
                "reasoning_level": sample.expected.reasoning_level,
                "evidence_strength": sample.expected.evidence_strength,
                "likely_fallacies": sample.expected.likely_fallacies,
            },
            "success": False,
            "latency_ms": latency_ms,
            "error": str(e),
            "scores": {},
            "fallacies": [],
            "observations": [],
            "insight": "",
        }


def run_benchmark_sync(
    dataset_path: str | None = None,
    *,
    engine: AnalysisEngine | None = None,
) -> list[dict]:
    """Synchronous wrapper for run_benchmark."""
    return asyncio.run(run_benchmark(dataset_path, engine=engine))
