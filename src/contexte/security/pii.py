"""Regex-based PII scanner."""

from __future__ import annotations

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
    ("pii:email", "medium", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    (
        "pii:phone",
        "low",
        re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}(?!\w)"),
    ),
    ("pii:credit_card_candidate", "medium", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("pii:ssn_candidate", "medium", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    (
        "pii:ip_address",
        "low",
        re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    ),
    ("pii:iban_candidate", "medium", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")),
]


def find_pii(text: str) -> list[PatternMatch]:
    matches: list[PatternMatch] = []
    for label, severity, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            candidate = match.group(0)
            if label == "pii:credit_card_candidate" and not _looks_like_card(candidate):
                continue
            matches.append(
                PatternMatch(
                    label=label,
                    severity=severity,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                )
            )
    return matches


def _looks_like_card(candidate: str) -> bool:
    digits = [int(char) for char in candidate if char.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        value = digit
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        checksum += value
    return checksum % 10 == 0
