"""Text normalization utilities."""

from __future__ import annotations

import re
import unicodedata

_NULL_BYTES = re.compile("\x00+")
_HORIZONTAL_WS = re.compile(r"[\t\r\f\v ]+")
_TOO_MANY_BLANKS = re.compile(r"\n{3,}")


def normalize_text(text: str, *, preserve_line_breaks: bool = True) -> str:
    text = unicodedata.normalize("NFC", text)
    text = _NULL_BYTES.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_HORIZONTAL_WS.sub(" ", line).strip() for line in text.split("\n")]
    normalized = "\n".join(lines) if preserve_line_breaks else " ".join(lines)
    normalized = _TOO_MANY_BLANKS.sub("\n\n", normalized)
    return normalized.strip()


def split_paragraphs(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]


def estimate_token_count(text: str) -> int:
    # Conservative approximation used only for local quality metadata.
    return max(1, round(len(text.split()) * 1.3)) if text.strip() else 0
