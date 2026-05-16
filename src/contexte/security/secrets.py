"""Regex- and entropy-based secret scanner with broad provider coverage."""

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
    confidence: float = 0.5


_PATTERNS: list[tuple[str, str, float, re.Pattern[str]]] = [
    # AWS
    ("secret:aws_access_key", "high", 0.95, re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "secret:aws_secret_key",
        "critical",
        0.7,
        re.compile(r"(?i)aws(.{0,20})?(?:secret|access).{0,5}[:=]\s*[\"']?([A-Za-z0-9/+=]{40})"),
    ),
    # GitHub
    ("secret:github_token", "high", 0.95, re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    (
        "secret:github_fine_grained",
        "high",
        0.9,
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
    ),
    # Slack / Discord
    ("secret:slack_token", "high", 0.9, re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "secret:slack_webhook",
        "high",
        0.9,
        re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),
    ),
    (
        "secret:discord_webhook",
        "high",
        0.9,
        re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+"),
    ),
    # AI providers
    (
        "secret:openai_api_key",
        "critical",
        0.95,
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "secret:anthropic_api_key",
        "critical",
        0.95,
        re.compile(r"\bsk-ant-(?:api|admin)\d{2}-[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "secret:google_api_key",
        "high",
        0.85,
        re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    ),
    # GCP
    (
        "secret:gcp_service_account",
        "critical",
        0.95,
        re.compile(r'"type":\s*"service_account"', re.I),
    ),
    # Stripe
    (
        "secret:stripe_secret",
        "critical",
        0.95,
        re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "secret:stripe_publishable",
        "low",
        0.6,
        re.compile(r"\bpk_(?:live|test)_[A-Za-z0-9]{20,}\b"),
    ),
    # Twilio / SendGrid / Mailgun
    (
        "secret:twilio_account_sid",
        "medium",
        0.7,
        re.compile(r"\bAC[a-f0-9]{32}\b"),
    ),
    (
        "secret:sendgrid_api_key",
        "high",
        0.9,
        re.compile(r"\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
    ),
    # JWT (often holds tokens)
    (
        "secret:jwt",
        "medium",
        0.85,
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    # SSH / TLS private keys
    (
        "secret:private_key",
        "critical",
        0.99,
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----"
        ),
    ),
    # Generic API key assignment
    (
        "secret:api_key",
        "medium",
        0.6,
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|bearer)\b\s*[:=]\s*"
            r"[\"']?[A-Za-z0-9_./+=-]{16,}"
        ),
    ),
    # Database URLs that embed credentials
    (
        "secret:db_url_with_credentials",
        "high",
        0.85,
        re.compile(
            r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqp|amqps)://"
            r"[^:\s]+:[^@\s]+@[^/\s]+",
            re.I,
        ),
    ),
]
_LONG_TOKEN = re.compile(r"\b[A-Za-z0-9_+/=-]{32,}\b")


def find_secrets(
    text: str,
    *,
    allowlist: frozenset[str] | None = None,
    entropy_threshold: float = 3.8,
) -> list[PatternMatch]:
    """Return secret-like matches in ``text``.

    Parameters
    ----------
    text:
        Free text to scan.
    allowlist:
        Optional literal substrings to ignore (e.g. fixture tokens).
    entropy_threshold:
        Minimum Shannon entropy (bits/char) for the high-entropy fallback.
    """

    matches: list[PatternMatch] = []
    allowlist = allowlist or frozenset()
    occupied: list[range] = []
    for label, severity, confidence, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            candidate = match.group(0)
            if candidate in allowlist:
                continue
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
            occupied.append(range(match.start(), match.end()))
    for match in _LONG_TOKEN.finditer(text):
        candidate = match.group(0)
        if candidate in allowlist:
            continue
        if any(match.start() in span or match.end() - 1 in span for span in occupied):
            continue
        entropy = _entropy(candidate)
        if entropy < entropy_threshold:
            continue
        matches.append(
            PatternMatch(
                label="secret:high_entropy_token",
                severity="medium",
                start=match.start(),
                end=match.end(),
                text=candidate,
                # Map entropy [3.8, 5.5] -> confidence [0.55, 0.9] linearly.
                confidence=min(0.9, 0.55 + (entropy - 3.8) * 0.2),
            )
        )
    return matches


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    frequencies = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in frequencies.values())
