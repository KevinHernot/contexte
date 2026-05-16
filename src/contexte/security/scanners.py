"""Aggregate security scanning helpers."""

from __future__ import annotations

from typing import Protocol, cast

from contexte.core import ids
from contexte.ir.models import (
    ChunkSecurity,
    ContextChunk,
    ContextDocument,
    SecurityFinding,
    SecuritySummary,
    SourceSpan,
)
from contexte.security.pii import find_pii
from contexte.security.prompt_injection import find_prompt_injection, prompt_injection_score
from contexte.security.secrets import find_secrets


class MatchLike(Protocol):
    label: str
    severity: str
    start: int
    end: int
    text: str


def scan_text(
    document_id: str,
    text: str,
    *,
    chunk_id: str | None = None,
    pii: bool = True,
    secrets: bool = True,
    prompt_injection: bool = True,
) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    raw_matches: list[tuple[str, MatchLike]] = []
    if pii:
        raw_matches.extend(("pii", cast(MatchLike, match)) for match in find_pii(text))
    if secrets:
        raw_matches.extend(("secret", cast(MatchLike, match)) for match in find_secrets(text))
    if prompt_injection:
        raw_matches.extend(
            ("prompt_injection", cast(MatchLike, match)) for match in find_prompt_injection(text)
        )
    for index, (finding_type, match) in enumerate(raw_matches):
        findings.append(
            SecurityFinding(
                id=ids.finding_id(document_id, match.label, index, chunk_id),
                document_id=document_id,
                chunk_id=chunk_id,
                type=finding_type,  # type: ignore[arg-type]
                label=match.label,
                severity=match.severity,  # type: ignore[arg-type]
                text_preview=_preview(text, match.start, match.end, mask=finding_type == "secret"),
                location=SourceSpan(start=match.start, end=match.end),
                explanation=_explanation(finding_type, match.label),
                recommendation=_recommendation(finding_type, match.label),
            )
        )
    return findings


def scan_document_security(
    document: ContextDocument,
    *,
    pii: bool = True,
    secrets: bool = True,
    prompt_injection: bool = True,
) -> list[SecurityFinding]:
    text = "\n\n".join(block.text or block.markdown or "" for block in document.blocks)
    findings = scan_text(
        document.id, text, pii=pii, secrets=secrets, prompt_injection=prompt_injection
    )
    document.security = summary_from_findings(findings)
    return findings


def scan_chunk_security(
    chunk: ContextChunk,
    *,
    pii: bool = True,
    secrets: bool = True,
    prompt_injection: bool = True,
) -> list[SecurityFinding]:
    findings = scan_text(
        chunk.document_id,
        chunk.text,
        chunk_id=chunk.id,
        pii=pii,
        secrets=secrets,
        prompt_injection=prompt_injection,
    )
    labels = sorted({finding.label for finding in findings})
    chunk.security = ChunkSecurity(
        pii_count=sum(1 for finding in findings if finding.type == "pii"),
        secret_count=sum(1 for finding in findings if finding.type == "secret"),
        prompt_injection_score=prompt_injection_score(
            sum(1 for finding in findings if finding.type == "prompt_injection")
        ),
        labels=labels,
    )
    return findings


def summary_from_findings(findings: list[SecurityFinding]) -> SecuritySummary:
    return SecuritySummary(
        pii_count=sum(1 for finding in findings if finding.type == "pii"),
        secret_count=sum(1 for finding in findings if finding.type == "secret"),
        prompt_injection_score=prompt_injection_score(
            sum(1 for finding in findings if finding.type == "prompt_injection")
        ),
        labels=sorted({finding.label for finding in findings}),
    )


def _preview(text: str, start: int, end: int, *, mask: bool) -> str:
    prefix = text[max(0, start - 24) : start]
    value = text[start:end]
    suffix = text[end : min(len(text), end + 24)]
    if mask and len(value) > 8:
        value = f"{value[:4]}…{value[-4:]}"
    return f"{prefix}{value}{suffix}".strip()


def _explanation(finding_type: str, label: str) -> str:
    if finding_type == "secret":
        return f"Detected potential {label} (API key, token, or secret) using pattern matching."
    if finding_type == "pii":
        return f"Detected potential {label} (name, email, phone, or ID) using regular expressions."
    if finding_type == "prompt_injection":
        return "Detected potential adversarial text that may attempt to override or hijack LLM system instructions."
    return f"Detected security finding of type {finding_type} labeled as {label}."


def _recommendation(finding_type: str, label: str) -> str:
    if finding_type == "secret":
        return "Rotate the suspected secret and remove it from source material before sharing."
    if finding_type == "pii":
        return "Review whether this personal data is necessary for the intended context use."
    if finding_type == "prompt_injection":
        return "Treat this content as untrusted instructions and isolate it from system/developer prompts."
    return f"Review finding {label}."
