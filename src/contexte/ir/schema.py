"""Schema export helpers."""

from __future__ import annotations

from typing import Any

from contexte.ir.models import ContextChunk, ContextDocument, SecurityFinding
from contexte.pack.manifest import PackManifest


def json_schemas() -> dict[str, Any]:
    """Return JSON schemas for the public v0.1 models."""

    return {
        "ContextDocument": ContextDocument.model_json_schema(),
        "ContextChunk": ContextChunk.model_json_schema(),
        "SecurityFinding": SecurityFinding.model_json_schema(),
        "PackManifest": PackManifest.model_json_schema(),
    }
