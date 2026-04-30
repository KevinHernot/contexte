"""Exact deduplication helpers."""

from __future__ import annotations

from collections import Counter

from contexte.core.hashing import sha256_text
from contexte.ir.models import ContextChunk
from contexte.normalizers.text import normalize_text


def chunk_text_hash(chunk: ContextChunk) -> str:
    return sha256_text(normalize_text(chunk.text, preserve_line_breaks=False).lower())


def annotate_duplicate_chunks(chunks: list[ContextChunk]) -> float:
    hashes = [chunk_text_hash(chunk) for chunk in chunks]
    counts = Counter(hashes)
    duplicates = 0
    for chunk, digest in zip(chunks, hashes, strict=True):
        count = counts[digest]
        if count > 1:
            duplicates += 1
            chunk.quality.duplicate_score = min(1.0, (count - 1) / count)
            if "duplicate_chunk_exact" not in chunk.quality.warnings:
                chunk.quality.warnings.append("duplicate_chunk_exact")
        else:
            chunk.quality.duplicate_score = 0.0
    return duplicates / len(chunks) if chunks else 0.0
