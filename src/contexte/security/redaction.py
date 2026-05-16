"""Optional redaction helpers for PII and secret findings.

Core Contexte v0.1 marks security findings as metadata and never rewrites the
underlying content during build. This module is opt-in: callers (such as the
``ctx export --redact`` flag) can use it to produce derived artifacts that are
safer to share, without mutating the canonical Context Pack.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from contexte.ir.models import SecurityFinding

if TYPE_CHECKING:
    from contexte.ir.models import ContextDocument

#: Default set of finding types that should be redacted when redaction is enabled.
DEFAULT_REDACTABLE_TYPES: frozenset[str] = frozenset({"pii", "secret"})

#: Marker used when a finding does not expose its location span. The marker
#: includes the label so reviewers can still understand what was redacted.
PLACEHOLDER_FORMAT = "[REDACTED:{label}]"


def redact_text(
    text: str,
    findings: list[SecurityFinding],
    *,
    redact_types: frozenset[str] | set[str] = DEFAULT_REDACTABLE_TYPES,
) -> str:
    """Return ``text`` with redactable findings replaced by labelled placeholders.

    Findings without a ``location`` span are ignored, since their position in
    the chunk text is unknown. Overlapping findings are resolved by replacing
    the longest span first, then dropping any later finding whose span is now
    invalid.

    Parameters
    ----------
    text:
        The chunk or document text to redact.
    findings:
        Security findings produced by :func:`contexte.security.scanners.scan_text`.
    redact_types:
        Finding types eligible for redaction. Defaults to PII and secrets.
        Prompt-injection findings are intentionally excluded by default since
        they are typically handled at prompt-construction time.
    """

    if not text or not findings:
        return text

    eligible: list[tuple[int, int, str]] = []
    for finding in findings:
        if finding.type not in redact_types:
            continue
        location = finding.location
        if location is None or location.start is None or location.end is None:
            continue
        eligible.append((location.start, location.end, finding.label))

    if not eligible:
        return text

    # Sort by start descending so replacements do not shift earlier offsets.
    eligible.sort(key=lambda item: (item[0], -(item[1] - item[0])), reverse=True)

    redacted = text
    last_start = len(text) + 1
    for start, end, label in eligible:
        if start < 0 or end > len(redacted) or start >= end:
            continue
        if end > last_start:  # overlaps with an already-applied redaction
            continue
        placeholder = PLACEHOLDER_FORMAT.format(label=label)
        redacted = redacted[:start] + placeholder + redacted[end:]
        last_start = start
    return redacted


def redact_chunk_text(
    text: str,
    findings: list[SecurityFinding],
    chunk_id: str,
    *,
    redact_types: frozenset[str] | set[str] = DEFAULT_REDACTABLE_TYPES,
) -> str:
    """Redact a single chunk's text using only findings attached to it."""

    chunk_findings = [finding for finding in findings if finding.chunk_id == chunk_id]
    return redact_text(text, chunk_findings, redact_types=redact_types)


def redact_document(
    doc: ContextDocument,
    findings: list[SecurityFinding],
    *,
    redact_types: frozenset[str] | set[str] = DEFAULT_REDACTABLE_TYPES,
) -> ContextDocument:
    """Return a copy of ``doc`` with all its blocks redacted."""
    from contexte.ir.models import Block
    
    new_blocks = []
    for block in doc.blocks:
        block_findings = [f for f in findings if f.block_id == block.id]
        new_text = redact_text(block.text or "", block_findings, redact_types=redact_types)
        new_markdown = redact_text(block.markdown or "", block_findings, redact_types=redact_types)
        new_blocks.append(
            Block(
                id=block.id,
                type=block.type,
                text=new_text or None,
                markdown=new_markdown or None,
                level=block.level,
                metadata=block.metadata,
            )
        )
    
    return doc.model_copy(update={"blocks": new_blocks})
