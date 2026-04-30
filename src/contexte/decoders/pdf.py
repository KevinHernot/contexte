"""PDF decoder using pypdf with a conservative text fallback."""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

from contexte.decoders.base import BaseDecoder, DecodeContext
from contexte.ir.models import ContextDocument, ExtractionError
from contexte.normalizers.text import normalize_text, split_paragraphs

_PDF_STRING = re.compile(rb"\(([^()]{3,})\)")


class PdfDecoder(BaseDecoder):
    id = "pdf"
    supported_extensions: ClassVar[set[str]] = {".pdf"}
    supported_media_types: ClassVar[set[str]] = {"application/pdf"}

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        blocks = []
        errors: list[ExtractionError] = []
        index = 0
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path), strict=False)
            for page_index, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                except Exception as exc:  # pragma: no cover - depends on PDF internals
                    errors.append(
                        ExtractionError(
                            code="pdf_page_extract_failed",
                            message=f"Failed to extract page {page_index}: {exc}",
                            severity="warning",
                            location=f"page:{page_index}",
                        )
                    )
                    continue
                for paragraph in split_paragraphs(page_text):
                    blocks.append(
                        self.block(
                            context,
                            index,
                            "paragraph",
                            normalize_text(paragraph),
                            page=page_index,
                            confidence=0.85,
                        )
                    )
                    index += 1
        except Exception as exc:
            errors.append(
                ExtractionError(
                    code="pdf_decode_failed",
                    message=f"pypdf could not decode the file: {exc}",
                    severity="warning",
                )
            )

        if not blocks:
            fallback_text = self._fallback_text(path)
            for paragraph in split_paragraphs(fallback_text):
                blocks.append(
                    self.block(
                        context, index, "paragraph", normalize_text(paragraph), confidence=0.35
                    )
                )
                index += 1
            if blocks:
                errors.append(
                    ExtractionError(
                        code="pdf_fallback_text_extraction",
                        message="Used low-confidence PDF string fallback extraction.",
                        severity="warning",
                    )
                )
            else:
                errors.append(
                    ExtractionError(
                        code="pdf_no_text_extracted",
                        message="No text was extracted from the PDF. OCR is not part of v0.1 core.",
                        severity="warning",
                    )
                )

        return self.make_document(path, context, blocks, title=path.stem, errors=errors)

    def _fallback_text(self, path: Path) -> str:
        data = path.read_bytes()
        matches = []
        for match in _PDF_STRING.finditer(data):
            raw = match.group(1).replace(rb"\\(", b"(").replace(rb"\\)", b")")
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1", errors="ignore")
            if any(char.isalpha() for char in text):
                matches.append(text)
        return "\n\n".join(matches)
