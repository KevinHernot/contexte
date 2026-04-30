"""Chunker protocol and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from contexte.core import ids
from contexte.ir.models import Block, ChunkQuality, ChunkSourceRef, ContextChunk, ContextDocument
from contexte.normalizers.text import estimate_token_count, normalize_text


@dataclass(frozen=True)
class ChunkerConfig:
    max_chars: int = 3000
    overlap_chars: int = 200


class Chunker(Protocol):
    id: str

    def chunk(self, document: ContextDocument) -> list[ContextChunk]: ...


def block_text(block: Block) -> str:
    text = block.markdown if block.type in {"code", "table"} and block.markdown else block.text
    return normalize_text(text or "")


def make_chunk(
    document: ContextDocument,
    strategy: str,
    index: int,
    blocks: list[Block],
    text: str,
    *,
    title: str | None = None,
    section_path: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ContextChunk:
    refs = [source_ref_for_blocks(document, blocks)]
    clean_text = normalize_text(text)
    confidence_values = [block.confidence for block in blocks if block.confidence is not None]
    extraction_confidence = (
        sum(confidence_values) / len(confidence_values) if confidence_values else None
    )
    return ContextChunk(
        id=ids.chunk_id(document.id, strategy, index),
        document_id=document.id,
        text=clean_text,
        title=title or document.title,
        section_path=section_path or [],
        source_refs=refs,
        token_count_estimate=estimate_token_count(clean_text),
        char_count=len(clean_text),
        metadata={"chunker": strategy},
        quality=ChunkQuality(
            extraction_confidence=extraction_confidence,
            has_citation=bool(refs),
            warnings=warnings or [],
        ),
    )


def source_ref_for_blocks(document: ContextDocument, blocks: list[Block]) -> ChunkSourceRef:
    pages = [block.page for block in blocks if block.page is not None]
    line_starts = [
        block.source_span.line_start
        for block in blocks
        if block.source_span and block.source_span.line_start
    ]
    line_ends = [
        block.source_span.line_end
        for block in blocks
        if block.source_span and block.source_span.line_end
    ]
    return ChunkSourceRef(
        document_id=document.id,
        block_ids=[block.id for block in blocks],
        source_uri=document.source.uri,
        page_start=min(pages) if pages else None,
        page_end=max(pages) if pages else None,
        line_start=min(line_starts) if line_starts else None,
        line_end=max(line_ends) if line_ends else None,
    )


def split_large_text(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end >= len(text):
            tail = text[start:].strip()
            if tail:
                parts.append(tail)
            break
        split_at = text.rfind("\n\n", start, end)
        if split_at <= start + max_chars // 2:
            split_at = text.rfind(" ", start, end)
        if split_at <= start:
            split_at = end
        parts.append(text[start:split_at].strip())
        next_start = split_at - overlap_chars if overlap_chars > 0 else split_at
        if next_start <= start:
            next_start = split_at
        start = next_start
    return [part for part in parts if part]
