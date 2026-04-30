"""Reusable eval metric helpers."""

from __future__ import annotations

from statistics import median

from contexte.core.hashing import sha256_text
from contexte.ir.models import ContextChunk
from contexte.normalizers.text import normalize_text


def average(values: list[int]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def median_int(values: list[int]) -> float:
    return float(median(values)) if values else 0.0


def duplicate_chunk_ratio(chunks: list[ContextChunk]) -> float:
    if not chunks:
        return 0.0
    hashes = [
        sha256_text(normalize_text(chunk.text, preserve_line_breaks=False).lower())
        for chunk in chunks
    ]
    duplicate_count = len(hashes) - len(set(hashes))
    return duplicate_count / len(chunks)
