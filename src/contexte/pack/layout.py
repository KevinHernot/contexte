"""Canonical `.ctxpack` internal paths."""

from __future__ import annotations

MANIFEST = "manifest.json"
DOCUMENTS_JSONL = "documents/documents.jsonl"
CHUNKS_JSONL = "chunks/chunks.jsonl"
BUILD_REPORT_JSON = "reports/build-report.json"
SECURITY_FINDINGS_JSONL = "security/findings.jsonl"
SIGNATURE_JSON = "signature.json"
SOURCES_JSONL = "metadata/sources.jsonl"
PIPELINE_JSON = "metadata/pipeline.json"
CHECKSUMS_JSON = "metadata/checksums.json"
EVAL_REPORT_JSON = "eval/basic-report.json"
EVAL_REPORT_HTML = "eval/basic-report.html"
NORMALIZED_MARKDOWN_DIR = "normalized/markdown"
REQUIRED_FILES = {
    MANIFEST,
    DOCUMENTS_JSONL,
    CHUNKS_JSONL,
    BUILD_REPORT_JSON,
    SECURITY_FINDINGS_JSONL,
    SOURCES_JSONL,
    PIPELINE_JSON,
    CHECKSUMS_JSON,
}
