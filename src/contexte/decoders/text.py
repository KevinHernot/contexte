"""Plain text decoder."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from contexte.decoders.base import BaseDecoder, DecodeContext, read_text_with_fallback
from contexte.ir.models import ContextDocument, ExtractionError
from contexte.normalizers.text import normalize_text, split_paragraphs


class TextDecoder(BaseDecoder):
    id = "text"
    supported_extensions: ClassVar[set[str]] = {".txt"}
    supported_media_types: ClassVar[set[str]] = {"text/plain"}

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        raw, encoding = read_text_with_fallback(path)
        paragraphs = split_paragraphs(raw)
        blocks = []
        line_cursor = 1
        for index, paragraph in enumerate(paragraphs):
            line_count = max(1, paragraph.count("\n") + 1)
            blocks.append(
                self.block(
                    context,
                    index,
                    "paragraph",
                    normalize_text(paragraph),
                    line_start=line_cursor,
                    line_end=line_cursor + line_count - 1,
                )
            )
            line_cursor += line_count + 1
        errors: list[ExtractionError] = []
        if not blocks:
            errors.append(
                ExtractionError(
                    code="empty_text",
                    message="No text content was extracted from the file.",
                    severity="warning",
                )
            )
        return self.make_document(
            path,
            context,
            blocks,
            title=path.stem,
            errors=errors,
            metadata_extra={"encoding": encoding},
        )
