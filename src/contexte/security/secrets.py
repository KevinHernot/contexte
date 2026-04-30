"""Regex-based secret scanner."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PatternMatch:
    label: str
    severity: str
    start: int
    end: int
    text: str


_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("secret:aws_access_key", "high", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("secret:github_token", "high", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("secret:slack_token", "high", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "secret:private_key",
        "critical",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)?PRIVATE KEY-----"),
    ),
    (
        "secret:api_key",
        "medium",
        re.compile(r"(?i)\b(?:api[_-]?key|token|secret)\b\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{16,}"),
    ),
]
_LONG_TOKEN = re.compile(r"\b[A-Za-z0-9_+/=-]{32,}\b")


def find_secrets(text: str) -> list[PatternMatch]:
    matches: list[PatternMatch] = []
    occupied: list[range] = []
    for label, severity, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            matches.append(
                PatternMatch(label, severity, match.start(), match.end(), match.group(0))
            )
            occupied.append(range(match.start(), match.end()))
    for match in _LONG_TOKEN.finditer(text):
        if any(match.start() in span or match.end() - 1 in span for span in occupied):
            continue
        candidate = match.group(0)
        if _entropy(candidate) >= 3.8:
            matches.append(
                PatternMatch(
                    "secret:high_entropy_token",
                    "medium",
                    match.start(),
                    match.end(),
                    candidate,
                )
            )
    return matches


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    frequencies = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in frequencies.values())
