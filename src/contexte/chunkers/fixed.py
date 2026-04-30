"""Fixed-size chunker."""

from __future__ import annotations

from dataclasses import dataclass, field

from contexte.chunkers.base import ChunkerConfig, block_text, make_chunk, split_large_text
from contexte.ir.models import Block, ContextChunk, ContextDocument


@dataclass
class FixedChunker:
    config: ChunkerConfig = field(default_factory=ChunkerConfig)
    id: str = "fixed"

    def chunk(self, document: ContextDocument) -> list[ContextChunk]:
        chunks: list[ContextChunk] = []
        current_blocks: list[Block] = []
        current_parts: list[str] = []

        def flush() -> None:
            nonlocal current_blocks, current_parts
            text = "\n\n".join(current_parts).strip()
            if text and current_blocks:
                for part in split_large_text(
                    text, self.config.max_chars, self.config.overlap_chars
                ):
                    chunks.append(
                        make_chunk(
                            document,
                            self.id,
                            len(chunks),
                            current_blocks,
                            part,
                        )
                    )
            current_blocks = []
            current_parts = []

        for block in document.blocks:
            text = block_text(block)
            if not text:
                continue
            if block.type in {"code", "table"} and len(text) > self.config.max_chars:
                flush()
                for part in split_large_text(
                    text, self.config.max_chars, self.config.overlap_chars
                ):
                    chunks.append(make_chunk(document, self.id, len(chunks), [block], part))
                continue
            candidate = "\n\n".join([*current_parts, text]).strip()
            if current_parts and len(candidate) > self.config.max_chars:
                flush()
            current_blocks.append(block)
            current_parts.append(text)
        flush()
        return chunks
