"""Stable ID generation."""

from __future__ import annotations

import re

from contexte.core.hashing import sha256_text

_NON_WORD = re.compile(r"[^a-zA-Z0-9_-]+")


def normalize_uri_for_id(uri: str) -> str:
    return _NON_WORD.sub("_", uri).strip("_").lower()


def document_id(source_sha256: str, uri: str) -> str:
    """Create a stable document ID from source content and normalized URI."""

    base = sha256_text(f"{source_sha256}:{normalize_uri_for_id(uri)}")
    return f"doc_{base[:16]}"


def block_id(document_id_value: str, index: int) -> str:
    short = document_id_value.removeprefix("doc_")[:16]
    return f"blk_{short}_{index:06d}"


def chunk_id(document_id_value: str, strategy: str, index: int) -> str:
    short = document_id_value.removeprefix("doc_")[:16]
    strategy_slug = _NON_WORD.sub("_", strategy).strip("_").lower() or "chunk"
    return f"chk_{short}_{strategy_slug}_{index:06d}"


def finding_id(
    document_id_value: str, label: str, index: int, chunk_id_value: str | None = None
) -> str:
    seed = chunk_id_value or document_id_value
    label_slug = _NON_WORD.sub("_", label).strip("_").lower() or "finding"
    return f"fnd_{sha256_text(f'{seed}:{label_slug}:{index}')[:16]}"


def pack_id(source_summary_hash: str) -> str:
    return f"ctxpack_{source_summary_hash[:16]}"
