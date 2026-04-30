"""Markdown decoder with lightweight block extraction."""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

from contexte.decoders.base import BaseDecoder, DecodeContext, read_text_with_fallback
from contexte.ir.models import Block, ContextDocument, ExtractionError
from contexte.normalizers.text import normalize_text

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(.+?)\s*$")
_FENCE = re.compile(r"^\s*```")


class MarkdownDecoder(BaseDecoder):
    id = "markdown"
    supported_extensions: ClassVar[set[str]] = {".md", ".markdown"}
    supported_media_types: ClassVar[set[str]] = {"text/markdown", "text/x-markdown"}

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        raw, encoding = read_text_with_fallback(path)
        lines = raw.splitlines()
        blocks: list[Block] = []
        title: str | None = None
        index = 0
        paragraph: list[str] = []
        paragraph_start = 1
        in_code = False
        code_lines: list[str] = []
        code_start = 1

        def flush_paragraph(end_line: int) -> None:
            nonlocal index, paragraph, paragraph_start
            text = normalize_text("\n".join(paragraph))
            if text:
                blocks.append(
                    self.block(
                        context,
                        index,
                        "paragraph",
                        text,
                        markdown=text,
                        line_start=paragraph_start,
                        line_end=end_line,
                    )
                )
                index += 1
            paragraph = []

        for line_number, line in enumerate(lines, start=1):
            if _FENCE.match(line):
                if in_code:
                    code_lines.append(line)
                    code_text = "\n".join(code_lines).strip("\n")
                    blocks.append(
                        self.block(
                            context,
                            index,
                            "code",
                            code_text,
                            markdown=code_text,
                            line_start=code_start,
                            line_end=line_number,
                        )
                    )
                    index += 1
                    code_lines = []
                    in_code = False
                else:
                    flush_paragraph(line_number - 1)
                    in_code = True
                    code_start = line_number
                    code_lines = [line]
                continue
            if in_code:
                code_lines.append(line)
                continue

            heading = _HEADING.match(line)
            if heading:
                flush_paragraph(line_number - 1)
                level = len(heading.group(1))
                text = normalize_text(heading.group(2))
                if title is None and level == 1:
                    title = text
                blocks.append(
                    self.block(
                        context,
                        index,
                        "heading",
                        text,
                        markdown=line.strip(),
                        level=level,
                        line_start=line_number,
                        line_end=line_number,
                    )
                )
                index += 1
                continue

            list_item = _LIST_ITEM.match(line)
            if list_item:
                flush_paragraph(line_number - 1)
                text = normalize_text(list_item.group(1))
                blocks.append(
                    self.block(
                        context,
                        index,
                        "list_item",
                        text,
                        markdown=line.strip(),
                        line_start=line_number,
                        line_end=line_number,
                    )
                )
                index += 1
                continue

            if not line.strip():
                flush_paragraph(line_number - 1)
                paragraph_start = line_number + 1
                continue

            if not paragraph:
                paragraph_start = line_number
            paragraph.append(line)

        if in_code and code_lines:
            code_text = "\n".join(code_lines).strip("\n")
            blocks.append(
                self.block(
                    context,
                    index,
                    "code",
                    code_text,
                    markdown=code_text,
                    line_start=code_start,
                    line_end=len(lines),
                    confidence=0.8,
                )
            )
            index += 1
        flush_paragraph(len(lines))

        errors: list[ExtractionError] = []
        if not blocks:
            errors.append(
                ExtractionError(
                    code="empty_markdown",
                    message="No Markdown blocks were extracted.",
                    severity="warning",
                )
            )
        return self.make_document(
            path,
            context,
            blocks,
            title=title or path.stem,
            errors=errors,
            metadata_extra={"encoding": encoding},
        )
