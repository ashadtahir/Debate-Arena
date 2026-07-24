"""Reusable Hugging Face client — model loading, caching, inference."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

_MODEL_CACHE: dict[str, object] = {}


def _load_model(model_name: str) -> object:
    if model_name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading HF model: %s on device=%s", model_name, device)
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name, device=device)
    return _MODEL_CACHE[model_name]


def encode(text: str | list[str], *, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> np.ndarray:
    m = _load_model(model)
    return m.encode(text, convert_to_numpy=True)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
