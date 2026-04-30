"""CSV decoder."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import ClassVar

from contexte.decoders.base import BaseDecoder, DecodeContext
from contexte.ir.models import ContextDocument, ExtractionError
from contexte.normalizers.text import normalize_text


class CsvDecoder(BaseDecoder):
    id = "csv"
    supported_extensions: ClassVar[set[str]] = {".csv"}
    supported_media_types: ClassVar[set[str]] = {"text/csv", "application/csv"}

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        errors: list[ExtractionError] = []
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                sample = handle.read(4096)
                handle.seek(0)
                dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
                reader = csv.reader(handle, dialect)
                rows = list(reader)
        except Exception as exc:
            errors.append(
                ExtractionError(
                    code="csv_decode_failed",
                    message=f"CSV decoding failed: {exc}",
                    severity="error",
                )
            )
            rows = []

        blocks = []
        if rows:
            column_count = max(len(row) for row in rows)
            summary = f"CSV table with {len(rows)} rows and {column_count} columns."
            blocks.append(self.block(context, 0, "metadata", summary))
            header = rows[0]
            data_rows = rows[1:] if len(rows) > 1 else []
            index = 1
            for start in range(0, len(data_rows), 25):
                group = data_rows[start : start + 25]
                markdown = _rows_to_markdown(header, group)
                blocks.append(
                    self.block(
                        context,
                        index,
                        "table",
                        normalize_text(markdown),
                        markdown=markdown,
                        line_start=start + 2,
                        line_end=start + len(group) + 1,
                    )
                )
                index += 1
        else:
            errors.append(
                ExtractionError(
                    code="csv_empty",
                    message="No CSV rows were extracted.",
                    severity="warning",
                )
            )
        return self.make_document(
            path,
            context,
            blocks,
            title=path.stem,
            errors=errors,
            metadata_extra={
                "row_count": len(rows),
                "column_count": max((len(row) for row in rows), default=0),
            },
        )


def _rows_to_markdown(header: list[str], rows: list[list[str]]) -> str:
    width = max([len(header), *(len(row) for row in rows)])
    safe_header = [normalize_text(cell, preserve_line_breaks=False) for cell in header]
    safe_header += [""] * (width - len(safe_header))
    lines = ["| " + " | ".join(safe_header) + " |", "| " + " | ".join(["---"] * width) + " |"]
    for row in rows:
        safe_row = [normalize_text(cell, preserve_line_breaks=False) for cell in row]
        safe_row += [""] * (width - len(safe_row))
        lines.append("| " + " | ".join(safe_row) + " |")
    return "\n".join(lines)
