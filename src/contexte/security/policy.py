"""Security policy placeholders for future redaction and ACL support."""

from __future__ import annotations

from contexte.ir.models import SecurityFinding


def has_blocking_findings(findings: list[SecurityFinding]) -> bool:
    """Return whether findings should block a build under the current v0.1 policy.

    v0.1 marks findings and never blocks by default.
    """

    return False
