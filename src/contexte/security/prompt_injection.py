"""Prompt-injection heuristic scanner."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptInjectionMatch:
    label: str
    severity: str
    start: int
    end: int
    text: str


_PHRASES = [
    r"ignore (?:all )?(?:previous|prior) instructions",
    r"disregard (?:the )?(?:system|developer) message",
    r"reveal (?:the )?(?:hidden )?prompt",
    r"system prompt",
    r"developer message",
    r"tool call",
    r"override instructions",
    r"exfiltrate",
    r"send this data to",
    r"do not follow (?:the )?rules",
]
_PATTERN = re.compile("|".join(f"(?:{phrase})" for phrase in _PHRASES), re.I)


def find_prompt_injection(text: str) -> list[PromptInjectionMatch]:
    return [
        PromptInjectionMatch(
            label="prompt_injection:instruction_override",
            severity="medium",
            start=match.start(),
            end=match.end(),
            text=match.group(0),
        )
        for match in _PATTERN.finditer(text)
    ]


def prompt_injection_score(match_count: int) -> float:
    if match_count <= 0:
        return 0.0
    return min(1.0, match_count / 3.0)
