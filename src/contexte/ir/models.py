"""Context IR, chunk, security, and report models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from contexte.constants import CONTEXT_IR_SCHEMA_VERSION

Severity = Literal["info", "warning", "error", "critical"]
BlockType = Literal[
    "title",
    "heading",
    "paragraph",
    "list",
    "list_item",
    "table",
    "image",
    "code",
    "quote",
    "footnote",
    "page_break",
    "metadata",
    "unknown",
]
SecurityFindingType = Literal["pii", "secret", "prompt_injection", "policy"]
FindingSeverity = Literal["low", "medium", "high", "critical"]


class SourceSpan(BaseModel):
    start: int | None = None
    end: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    page_start: int | None = None
    page_end: int | None = None


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float
    coordinate_system: str = "page"


class SourceRef(BaseModel):
    uri: str
    type: str
    media_type: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None
    original_path: str | None = None


class Block(BaseModel):
    id: str
    type: BlockType
    text: str | None = None
    markdown: str | None = None
    html: str | None = None
    level: int | None = None
    page: int | None = None
    bbox: BoundingBox | None = None
    source_span: SourceSpan | None = None
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = None


class Lineage(BaseModel):
    decoder: str
    decoder_version: str | None = None
    pipeline_version: str
    pipeline_config_hash: str
    created_by: str = "contexte"


class SecuritySummary(BaseModel):
    pii_count: int = 0
    secret_count: int = 0
    prompt_injection_score: float | None = None
    labels: list[str] = Field(default_factory=list)


class ExtractionError(BaseModel):
    code: str
    message: str
    severity: Severity
    location: str | None = None


class ContextDocument(BaseModel):
    id: str
    schema_version: str = CONTEXT_IR_SCHEMA_VERSION
    source: SourceRef
    title: str | None = None
    language: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    extracted_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    blocks: list[Block]
    security: SecuritySummary = Field(default_factory=SecuritySummary)
    lineage: Lineage
    errors: list[ExtractionError] = Field(default_factory=list)


class ChunkSourceRef(BaseModel):
    document_id: str
    block_ids: list[str]
    source_uri: str
    page_start: int | None = None
    page_end: int | None = None
    line_start: int | None = None
    line_end: int | None = None


class ChunkSecurity(BaseModel):
    pii_count: int = 0
    secret_count: int = 0
    prompt_injection_score: float | None = None
    labels: list[str] = Field(default_factory=list)
    allowed_groups: list[str] = Field(default_factory=list)


class ChunkQuality(BaseModel):
    extraction_confidence: float | None = None
    chunk_coherence_score: float | None = None
    duplicate_score: float | None = None
    has_citation: bool = False
    warnings: list[str] = Field(default_factory=list)


class ContextChunk(BaseModel):
    id: str
    schema_version: str = CONTEXT_IR_SCHEMA_VERSION
    document_id: str
    text: str
    title: str | None = None
    section_path: list[str] = Field(default_factory=list)
    source_refs: list[ChunkSourceRef]
    token_count_estimate: int | None = None
    char_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    security: ChunkSecurity = Field(default_factory=ChunkSecurity)
    quality: ChunkQuality = Field(default_factory=ChunkQuality)


class SecurityFinding(BaseModel):
    id: str
    document_id: str
    chunk_id: str | None = None
    type: SecurityFindingType
    label: str
    severity: FindingSeverity
    text_preview: str | None = None
    location: SourceSpan | None = None
    recommendation: str | None = None


class BasicEvalReport(BaseModel):
    document_count: int
    chunk_count: int
    unsupported_file_count: int
    failed_file_count: int
    empty_document_count: int
    empty_chunk_count: int
    avg_chunk_chars: float
    median_chunk_chars: float
    max_chunk_chars: int
    chunks_without_source_refs: int
    chunks_without_citations_ratio: float
    duplicate_chunk_ratio: float
    pii_finding_count: int
    secret_finding_count: int
    prompt_injection_finding_count: int
    warnings: list[str]
    rag_readiness_score: int
    score_explanation: list[str]


class BuildReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: str = CONTEXT_IR_SCHEMA_VERSION
    source_root: str
    discovered_file_count: int
    supported_file_count: int
    unsupported_file_count: int
    failed_file_count: int
    empty_document_count: int = 0
    document_count: int
    chunk_count: int
    security_finding_count: int
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    created_at: datetime
