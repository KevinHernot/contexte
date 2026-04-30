"""JSONL chunk exporter."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from contexte.ir.serialize import write_jsonl
from contexte.pack.reader import PackReader
from contexte.security.redaction import redact_text


class JsonlExporter:
    id = "jsonl"

    def __init__(self, *, redact: bool = False) -> None:
        self.redact = redact

    def export(self, reader: PackReader, output: Path) -> None:
        findings_by_chunk: dict[str, list] = defaultdict(list)
        if self.redact:
            for finding in reader.iter_findings():
                if finding.chunk_id:
                    findings_by_chunk[finding.chunk_id].append(finding)

        rows = []
        for chunk in reader.iter_chunks():
            text = chunk.text
            if self.redact:
                text = redact_text(text, findings_by_chunk.get(chunk.id, []))
            first_ref = chunk.source_refs[0] if chunk.source_refs else None
            rows.append(
                {
                    "id": chunk.id,
                    "text": text,
                    "metadata": {
                        "document_id": chunk.document_id,
                        "source_uri": first_ref.source_uri if first_ref else None,
                        "title": chunk.title,
                        "section_path": chunk.section_path,
                        "page_start": first_ref.page_start if first_ref else None,
                        "page_end": first_ref.page_end if first_ref else None,
                        "line_start": first_ref.line_start if first_ref else None,
                        "line_end": first_ref.line_end if first_ref else None,
                        "redacted": self.redact,
                        **chunk.metadata,
                    },
                }
            )
        write_jsonl(output, rows)
