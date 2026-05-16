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
            if not text or not current_blocks:
                return

            # Avoid chunks that are just a single heading (orphans)
            if len(current_blocks) == 1 and current_blocks[0].type == "heading":
                # If there are no more blocks, we keep it, otherwise it should have been merged
                pass

            title = current_section_path[-1] if current_section_path else document.title
            
            # Simple quality heuristic
            score = 1.0
            labels = []
            if len(text) < 100:
                score -= 0.2
                labels.append("short_chunk")
            if len(text) > self.config.max_chars * 0.9:
                labels.append("large_chunk")

            for part in split_large_text(
                text, self.config.max_chars, self.config.overlap_chars
            ):
                chunk = make_chunk(
                    document,
                    self.id,
                    len(chunks),
                    current_blocks,
                    part,
                    title=title,
                    section_path=current_section_path,
                )
                chunk.quality.score = score
                chunk.quality.labels.extend(labels)
                chunks.append(chunk)
            
            current_blocks = []
            current_parts = []

        for block in document.blocks:
            text = block_text(block)
            if not text:
                continue
            
            if block.type == "heading":
                # If we have content, flush it before the new heading
                if current_parts and not (len(current_blocks) == 1 and current_blocks[0].type == "heading"):
                    flush()
                
                level = block.level or 1
                section_path = section_path[: max(0, level - 1)]
                section_path.append(text)
                current_section_path = section_path.copy()
                current_blocks.append(block)
                current_parts.append(text)
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
