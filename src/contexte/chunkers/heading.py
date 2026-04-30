"""Heading-aware chunker."""

from __future__ import annotations

from dataclasses import dataclass, field

from contexte.chunkers.base import ChunkerConfig, block_text, make_chunk, split_large_text
from contexte.ir.models import Block, ContextChunk, ContextDocument


@dataclass
class HeadingChunker:
    config: ChunkerConfig = field(default_factory=ChunkerConfig)
    id: str = "heading"

    def chunk(self, document: ContextDocument) -> list[ContextChunk]:
        chunks: list[ContextChunk] = []
        section_path: list[str] = []
        current_blocks: list[Block] = []
        current_parts: list[str] = []
        current_section_path: list[str] = []

        def flush() -> None:
            nonlocal current_blocks, current_parts, current_section_path
            text = "\n\n".join(current_parts).strip()
            if text and current_blocks:
                title = current_section_path[-1] if current_section_path else document.title
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
                            title=title,
                            section_path=current_section_path,
                        )
                    )
            current_blocks = []
            current_parts = []
            current_section_path = []

        for block in document.blocks:
            text = block_text(block)
            if not text:
                continue
            if block.type == "heading":
                flush()
                level = block.level or 1
                section_path = section_path[: max(0, level - 1)]
                section_path.append(text)
                current_section_path = section_path.copy()
                current_blocks = [block]
                current_parts = [text]
                continue

            if not current_section_path:
                current_section_path = section_path.copy()
            candidate = "\n\n".join([*current_parts, text]).strip()
            if current_parts and len(candidate) > self.config.max_chars:
                flush()
                current_section_path = section_path.copy()
            current_blocks.append(block)
            current_parts.append(text)
        flush()
        return chunks
