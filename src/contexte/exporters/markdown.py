"""Normalized Markdown exporter."""

from __future__ import annotations

from pathlib import Path

from contexte.ir.models import ContextDocument
from contexte.pack.reader import PackReader
from contexte.security.redaction import redact_text
from contexte.security.scanners import scan_text


class MarkdownExporter:
    id = "markdown"

    def __init__(self, *, redact: bool = False) -> None:
        self.redact = redact

    def export(self, reader: PackReader, output: Path) -> None:
        output.mkdir(parents=True, exist_ok=True)
        for document in reader.iter_documents():
            (output / f"{document.id}.md").write_text(
                document_to_markdown(document, redact=self.redact), encoding="utf-8"
            )


def document_to_markdown(document: ContextDocument, *, redact: bool = False) -> str:
    lines = ["---"]
    lines.append(f"document_id: {document.id}")
    lines.append(f"source_uri: {_yaml_quote(document.source.uri)}")
    lines.append(f"title: {_yaml_quote(document.title or document.id)}")
    if redact:
        lines.append("redacted: true")
    lines.append("---")
    lines.append("")
    for block in document.blocks:
        text = block.markdown or block.text or ""
        if not text.strip():
            continue
        heading = block.text or text if block.type == "heading" else None
        if redact:
            findings = scan_text(document.id, text)
            text = redact_text(text, findings)
            if heading is not None:
                heading_findings = scan_text(document.id, heading)
                heading = redact_text(heading, heading_findings)
        if block.type == "heading":
            level = min(6, max(1, block.level or 1))
            lines.append(f"{'#' * level} {heading}")
        else:
            lines.append(text)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
