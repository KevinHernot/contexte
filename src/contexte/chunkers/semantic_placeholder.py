"""Semantic chunker placeholder for plugin-backed future support."""

from __future__ import annotations

from contexte.core.errors import ConfigError
from contexte.ir.models import ContextChunk, ContextDocument


class SemanticChunkerPlaceholder:
    id = "semantic"

    def chunk(self, document: ContextDocument) -> list[ContextChunk]:
        raise ConfigError("Semantic chunking requires plugin: contexte-semantic")
