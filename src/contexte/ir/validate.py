"""Model validation helpers."""

from __future__ import annotations

from contexte.ir.models import ContextChunk, ContextDocument
from contexte.pack.manifest import PackManifest


def validate_document(document: ContextDocument) -> list[str]:
    errors: list[str] = []
    if not document.id.startswith("doc_"):
        errors.append(f"document {document.id}: id must start with doc_")
    if not document.source.uri:
        errors.append(f"document {document.id}: source.uri is required")
    if not document.blocks:
        errors.append(f"document {document.id}: no blocks")
    return errors


def validate_chunk(chunk: ContextChunk) -> list[str]:
    errors: list[str] = []
    if not chunk.id.startswith("chk_"):
        errors.append(f"chunk {chunk.id}: id must start with chk_")
    if not chunk.document_id.startswith("doc_"):
        errors.append(f"chunk {chunk.id}: document_id must start with doc_")
    if not chunk.text.strip():
        errors.append(f"chunk {chunk.id}: text is empty")
    if chunk.char_count != len(chunk.text):
        errors.append(f"chunk {chunk.id}: char_count mismatch")
    if not chunk.source_refs:
        errors.append(f"chunk {chunk.id}: source_refs is empty")
    return errors


def validate_manifest(manifest: PackManifest) -> list[str]:
    errors: list[str] = []
    if not manifest.pack_id.startswith("ctxpack_"):
        errors.append("manifest pack_id must start with ctxpack_")
    if not manifest.features.has_documents:
        errors.append("manifest must declare has_documents")
    if not manifest.features.has_chunks:
        errors.append("manifest must declare has_chunks")
    return errors
