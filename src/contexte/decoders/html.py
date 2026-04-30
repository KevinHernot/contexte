"""HTML decoder."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from bs4 import BeautifulSoup

from contexte.decoders.base import BaseDecoder, DecodeContext, read_text_with_fallback
from contexte.ir.models import Block, ContextDocument, ExtractionError
from contexte.normalizers.text import normalize_text


class HtmlDecoder(BaseDecoder):
    id = "html"
    supported_extensions: ClassVar[set[str]] = {".html", ".htm"}
    supported_media_types: ClassVar[set[str]] = {"text/html"}

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        raw, encoding = read_text_with_fallback(path)
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = normalize_text(soup.title.get_text(" ")) if soup.title else path.stem
        blocks: list[Block] = []
        index = 0
        for node in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "code", "blockquote", "table"]
        ):
            name = node.name.lower()
            text = normalize_text(node.get_text(" ", strip=True))
            if not text:
                continue
            if name.startswith("h") and len(name) == 2 and name[1].isdigit():
                block_type = "heading"
                level = int(name[1])
            elif name == "li":
                block_type = "list_item"
                level = None
            elif name == "table":
                block_type = "table"
                level = None
            elif name in {"pre", "code"}:
                block_type = "code"
                level = None
            elif name == "blockquote":
                block_type = "quote"
                level = None
            else:
                block_type = "paragraph"
                level = None
            links = [a.get("href") for a in node.find_all("a") if a.get("href")]
            block = self.block(
                context,
                index,
                block_type,
                text,
                html=str(node),
                level=level,
            )
            if links:
                block.metadata["links"] = links
            blocks.append(block)
            index += 1

        errors: list[ExtractionError] = []
        if not blocks:
            text = normalize_text(soup.get_text(" "))
            if text:
                blocks.append(self.block(context, 0, "paragraph", text, html=raw, confidence=0.7))
            else:
                errors.append(
                    ExtractionError(
                        code="empty_html",
                        message="No visible HTML content was extracted.",
                        severity="warning",
                    )
                )
        return self.make_document(
            path,
            context,
            blocks,
            title=title,
            errors=errors,
            metadata_extra={"encoding": encoding},
        )
