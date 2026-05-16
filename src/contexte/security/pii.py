"""Regex-based PII scanner with FR-specific patterns and confidence scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PatternMatch:
    label: str
    severity: str
    start: int
    end: int
    text: str
    confidence: float = 0.5
    notes: tuple[str, ...] = field(default_factory=tuple)


# (label, severity, base_confidence, regex). Order matters: more specific patterns first
# so that overlapping generic patterns get filtered by the dedup pass.
_PATTERNS: list[tuple[str, str, float, re.Pattern[str]]] = [
    # PII identity – common
    ("pii:email", "medium", 0.95, re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    (
        "pii:phone",
        "low",
        0.45,
        re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}(?!\w)"),
    ),
    (
        "pii:phone_fr",
        "medium",
        0.85,
        re.compile(r"(?<!\w)(?:\+33\s?|0)[1-9](?:[\s.\-]?\d{2}){4}(?!\w)"),
    ),
    (
        "pii:credit_card_candidate",
        "medium",
        0.75,
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    ),
    ("pii:ssn_us_candidate", "medium", 0.7, re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    # FR-specific
    (
        "pii:nir_fr",
        "high",
        0.85,
        re.compile(r"(?<!\d)([12])\s?(\d{2})\s?(0[1-9]|1[0-2]|2[0-9]|3[0-9]|4[0-9])\s?"
                   r"(\d{2,3})\s?(\d{3})\s?(\d{3})(?:\s?(\d{2}))?(?!\d)"),
    ),
    (
        "pii:siret_fr",
        "medium",
        0.7,
        re.compile(r"(?<!\d)\d{3}\s?\d{3}\s?\d{3}\s?\d{5}(?!\d)"),
    ),
    (
        "pii:siren_fr",
        "low",
        0.55,
        re.compile(r"(?<!\d)\d{3}\s?\d{3}\s?\d{3}(?!\d)"),
    ),
    (
        "pii:passport_fr",
        "high",
        0.7,
        re.compile(r"\b\d{2}[A-Z]{2}\d{5}\b"),
    ),
    (
        "pii:cni_fr_candidate",
        "medium",
        0.55,
        re.compile(r"\b\d{12}\b"),
    ),
    # Network / device identifiers
    (
        "pii:ip_address",
        "low",
        0.6,
        re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    ),
    (
        "pii:ipv6_address",
        "low",
        0.55,
        re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}\b"),
    ),
    (
        "pii:mac_address",
        "low",
        0.7,
        re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    ),
    # Banking
    (
        "pii:iban_candidate",
        "medium",
        0.6,
        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
    ),
    # Tokens that look like JWT (often leak through logs/exports)
    (
        "pii:jwt_candidate",
        "medium",
        0.85,
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    # Likely physical address (FR + EN heuristic)
    (
        "pii:postal_address_fr",
        "low",
        0.4,
        re.compile(
            r"\b\d{1,4}[,\s]+(?:rue|avenue|av\.|boulevard|bd\.|impasse|allée|chemin|place|"
            r"route|rte\.)\s+[A-Z][\wÀ-ÿ'\-\s]{2,40}",
            re.I,
        ),
    ),
]


# Keywords that should *increase* confidence when found in a small window around a match.
_CONTEXT_BOOST: dict[str, tuple[str, ...]] = {
    "pii:nir_fr": ("nir", "sécurité sociale", "secu", "numéro de sécurité"),
    "pii:siret_fr": ("siret", "société", "entreprise", "siège"),
    "pii:siren_fr": ("siren", "rcs", "numéro d'entreprise"),
    "pii:passport_fr": ("passeport", "passport"),
    "pii:cni_fr_candidate": ("carte d'identité", "cni", "national identity"),
    "pii:iban_candidate": ("iban", "rib", "compte bancaire", "bic", "swift"),
    "pii:credit_card_candidate": ("card", "carte", "visa", "mastercard", "amex"),
    "pii:postal_address_fr": ("adresse", "address", "domicile"),
}


def find_pii(text: str, *, allowlist: frozenset[str] | None = None) -> list[PatternMatch]:
    """Detect PII matches in ``text``.

    Parameters
    ----------
    text:
        Free text to scan.
    allowlist:
        Optional set of literal substrings that must NOT be flagged. Useful for
        suppressing known-safe values (corporate test emails, fixture data).
    """

    matches: list[PatternMatch] = []
    allowlist = allowlist or frozenset()
    for label, severity, base_confidence, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            candidate = match.group(0)
            if candidate in allowlist:
                continue
            if label == "pii:credit_card_candidate" and not _luhn(candidate):
                continue
            if label == "pii:nir_fr" and not _looks_like_nir(candidate):
                continue
            if label == "pii:siret_fr" and not _luhn(candidate):
                continue
            if label == "pii:iban_candidate" and not _iban_checksum_ok(candidate):
                continue
            confidence = _adjust_confidence(text, match.start(), match.end(), label, base_confidence)
            matches.append(
                PatternMatch(
                    label=label,
                    severity=severity,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                    confidence=confidence,
                )
            )
    return _dedupe_overlaps(matches)


def _adjust_confidence(text: str, start: int, end: int, label: str, base: float) -> float:
    keywords = _CONTEXT_BOOST.get(label)
    if not keywords:
        return base
    window_start = max(0, start - 40)
    window_end = min(len(text), end + 40)
    window = text[window_start:window_end].lower()
    if any(keyword in window for keyword in keywords):
        return min(0.99, base + 0.15)
    return base


def _dedupe_overlaps(matches: list[PatternMatch]) -> list[PatternMatch]:
    """Drop weaker overlapping matches, keep the highest-severity/confidence span."""

    severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    ordered = sorted(
        matches,
        key=lambda m: (severity_rank.get(m.severity, 0), m.confidence, m.end - m.start),
        reverse=True,
    )
    kept: list[PatternMatch] = []
    for match in ordered:
        if any(_overlaps(match, other) for other in kept):
            continue
        kept.append(match)
    kept.sort(key=lambda m: m.start)
    return kept


def _overlaps(a: PatternMatch, b: PatternMatch) -> bool:
    return not (a.end <= b.start or b.end <= a.start)


def _luhn(candidate: str) -> bool:
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


def _looks_like_nir(candidate: str) -> bool:
    """Validate a French NIR (sécurité sociale) using the official key check.

    Accepts both 13- and 15-digit forms. The 2-digit key is computed as
    ``97 - (number mod 97)``. Corsican departments (2A/2B) are normalized.
    """

    digits_only = re.sub(r"\s+", "", candidate)
    # Normalize Corsica (2A/2B) which would otherwise contain letters.
    normalized = digits_only.replace("2A", "19").replace("2B", "18")
    if len(normalized) == 13:
        return all(c.isdigit() for c in normalized)
    if len(normalized) != 15 or not normalized.isdigit():
        return False
    try:
        body = int(normalized[:13])
        key = int(normalized[13:])
    except ValueError:
        return False
    return key == 97 - (body % 97)


def _iban_checksum_ok(candidate: str) -> bool:
    iban = candidate.replace(" ", "").upper()
    if len(iban) < 15 or len(iban) > 34:
        return False
    rearranged = iban[4:] + iban[:4]
    digits = []
    for char in rearranged:
        if char.isdigit():
            digits.append(char)
        elif char.isalpha():
            digits.append(str(ord(char) - 55))
        else:
            return False
    try:
        return int("".join(digits)) % 97 == 1
    except ValueError:
        return False
