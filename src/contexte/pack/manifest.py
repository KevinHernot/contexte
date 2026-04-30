"""`.ctxpack` manifest models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from contexte.constants import CONTEXT_VERSION, CTXPACK_SCHEMA_VERSION


class SourceSummary(BaseModel):
    source_root: str
    document_count: int
    chunk_count: int


class PackFeatures(BaseModel):
    has_documents: bool = True
    has_chunks: bool = True
    has_security_findings: bool = True
    has_eval: bool = False
    has_embeddings: bool = False


class PackManifest(BaseModel):
    schema_version: str = CTXPACK_SCHEMA_VERSION
    pack_id: str
    created_at: datetime
    created_by: str = "contexte"
    contexte_version: str = CONTEXT_VERSION
    source_summary: SourceSummary
    features: PackFeatures = Field(default_factory=PackFeatures)
    checksums: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
