"""JSON decoder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

from contexte.decoders.base import BaseDecoder, DecodeContext
from contexte.ir.models import ContextDocument, ExtractionError
from contexte.normalizers.text import normalize_text


class JsonDecoder(BaseDecoder):
    id = "json"
    supported_extensions: ClassVar[set[str]] = {".json"}
    supported_media_types: ClassVar[set[str]] = {"application/json"}

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        errors: list[ExtractionError] = []
        blocks = []
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(
                ExtractionError(
                    code="json_decode_failed",
                    message=f"Invalid JSON: {exc}",
                    severity="error",
                )
            )
            value = None

        if value is not None:
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                blocks.append(
                    self.block(context, 0, "metadata", f"JSON array with {len(value)} objects.")
                )
                index = 1
                for start in range(0, len(value), 20):
                    payload = json.dumps(
                        value[start : start + 20], ensure_ascii=False, indent=2, sort_keys=True
                    )
                    blocks.append(
                        self.block(
                            context,
                            index,
                            "code",
                            normalize_text(payload),
                            markdown=f"```json\n{payload}\n```",
                        )
                    )
                    index += 1
            else:
                payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
                blocks.append(
                    self.block(
                        context,
                        0,
                        "code",
                        normalize_text(payload),
                        markdown=f"```json\n{payload}\n```",
                    )
                )
        if not blocks:
            errors.append(
                ExtractionError(
                    code="json_empty",
                    message="No JSON content was extracted.",
                    severity="warning",
                )
            )
        return self.make_document(
            path,
            context,
            blocks,
            title=_title_from_json(path, value),
            errors=errors,
            metadata_extra={"json_type": type(value).__name__ if value is not None else "invalid"},
        )


def _title_from_json(path: Path, value: Any) -> str:
    if isinstance(value, dict):
        for key in ("title", "name", "id"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return path.stem
