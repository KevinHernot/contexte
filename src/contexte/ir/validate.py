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

    block_ids = set()
    for block in document.blocks:
        if block.id in block_ids:
            errors.append(f"document {document.id}: duplicate block id {block.id}")
        block_ids.add(block.id)

    for block in document.blocks:
        if block.parent_id and block.parent_id not in block_ids:
            errors.append(f"document {document.id}: block {block.id} parent {block.parent_id} not found")
        for child_id in block.children_ids:
            if child_id not in block_ids:
                errors.append(f"document {document.id}: block {block.id} child {child_id} not found")

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


def validate_pack_integrity(
    manifest: PackManifest, documents: list[ContextDocument], chunks: list[ContextChunk]
) -> list[str]:
    errors: list[str] = []
    doc_ids = {doc.id for doc in documents}
    
    # Check that manifest counts match
    if manifest.source_summary.document_count != len(documents):
        errors.append(f"Manifest document count mismatch: {manifest.source_summary.document_count} != {len(documents)}")
    if manifest.source_summary.chunk_count != len(chunks):
        errors.append(f"Manifest chunk count mismatch: {manifest.source_summary.chunk_count} != {len(chunks)}")

    # Check chunk document references
    for chunk in chunks:
        if chunk.document_id not in doc_ids:
            errors.append(f"Chunk {chunk.id} references missing document {chunk.document_id}")
            
    return errors
