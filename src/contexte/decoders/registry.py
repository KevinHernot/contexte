"""Decoder registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from contexte.decoders.base import Decoder
from contexte.decoders.csv import CsvDecoder
from contexte.decoders.docx import DocxDecoder
from contexte.decoders.html import HtmlDecoder
from contexte.decoders.json import JsonDecoder
from contexte.decoders.markdown import MarkdownDecoder
from contexte.decoders.pdf import PdfDecoder
from contexte.decoders.text import TextDecoder
from contexte.ir.models import SourceRef


@dataclass
class DecoderRegistry:
    decoders: list[Decoder] = field(default_factory=list)

    def register(self, decoder: Decoder) -> None:
        self.decoders.append(decoder)

    def decoder_for(self, source: SourceRef) -> Decoder | None:
        for decoder in self.decoders:
            if decoder.can_decode(source):
                return decoder
        extension = Path(source.original_path or source.uri).suffix.lower()
        for decoder in self.decoders:
            if extension in decoder.supported_extensions:
                return decoder
        return None

    def supported_extensions(self) -> set[str]:
        extensions: set[str] = set()
        for decoder in self.decoders:
            extensions.update(decoder.supported_extensions)
        return extensions


def default_registry() -> DecoderRegistry:
    registry = DecoderRegistry()
    for decoder in (
        MarkdownDecoder(),
        TextDecoder(),
        HtmlDecoder(),
        PdfDecoder(),
        DocxDecoder(),
        CsvDecoder(),
        JsonDecoder(),
    ):
        registry.register(cast(Decoder, decoder))
    return registry
