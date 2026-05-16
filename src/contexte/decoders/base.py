"""Decoder protocol and shared helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Protocol

from contexte.constants import CONTEXT_VERSION
from contexte.core import ids
from contexte.ir.models import (
    Block,
    ContextDocument,
    ExtractionError,
    Lineage,
    SourceRef,
    SourceSpan,
)
from contexte.normalizers.metadata import file_metadata, file_times


@dataclass(frozen=True)
class DecodeContext:
    source_root: Path
    document_id: str
    source_ref: SourceRef
    pipeline_config_hash: str
    extracted_at: datetime


class Decoder(Protocol):
    id: str
    supported_extensions: ClassVar[set[str]]
    supported_media_types: ClassVar[set[str]]

    def can_decode(self, source: SourceRef) -> bool: ...

    def explain_support(self, source: SourceRef) -> str: ...

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument: ...


class BaseDecoder:
    id: ClassVar[str] = "base"
    supported_extensions: ClassVar[set[str]] = set()
    supported_media_types: ClassVar[set[str]] = set()

    def can_decode(self, source: SourceRef) -> bool:
        extension = Path(source.original_path or source.uri).suffix.lower()
        media_type = source.media_type or ""
        return extension in self.supported_extensions or media_type in self.supported_media_types

    def explain_support(self, source: SourceRef) -> str:
        extension = Path(source.original_path or source.uri).suffix.lower()
        if self.can_decode(source):
            return f"Supported via {self.id} decoder (matches {extension})"
        return f"Not supported by {self.id} (no match for {extension})"

    def block(
        self,
        context: DecodeContext,
        index: int,
        block_type: str,
        text: str | None = None,
        *,
        markdown: str | None = None,
        html: str | None = None,
        level: int | None = None,
        page: int | None = None,
        line_start: int | None = None,
        line_end: int | None = None,
        confidence: float | None = 1.0,
    ) -> Block:
        span = SourceSpan(line_start=line_start, line_end=line_end, page_start=page, page_end=page)
        return Block(
            id=ids.block_id(context.document_id, index),
            type=block_type,  # type: ignore[arg-type]
            text=text,
            markdown=markdown,
            html=html,
            level=level,
            page=page,
            source_span=span,
            confidence=confidence,
        )

    def make_document(
        self,
        path: Path,
        context: DecodeContext,
        blocks: list[Block],
        *,
        title: str | None = None,
        errors: list[ExtractionError] | None = None,
        metadata_extra: dict[str, object] | None = None,
    ) -> ContextDocument:
        times = file_times(path)
        metadata = file_metadata(path, root=context.source_root)
        if metadata_extra:
            metadata.update(metadata_extra)
        return ContextDocument(
            id=context.document_id,
            source=context.source_ref,
            title=title,
            created_at=times["created_at"],
            modified_at=times["modified_at"],
            extracted_at=context.extracted_at.astimezone(UTC),
            metadata=metadata,
            blocks=blocks,
            lineage=Lineage(
                decoder=self.id,
                decoder_version=None,
                pipeline_version=CONTEXT_VERSION,
                pipeline_config_hash=context.pipeline_config_hash,
            ),
            errors=errors or [],
        )


def read_text_with_fallback(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "utf-8-replace"
