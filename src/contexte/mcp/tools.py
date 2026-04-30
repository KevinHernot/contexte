"""Local read-only helper tools that mirror future serving adapter surfaces."""

from __future__ import annotations

from typing import Any

from contexte.pack.reader import PackReader

READ_ONLY_TOOL_NAMES = (
    "search_context",
    "get_chunk",
    "get_source_metadata",
    "get_manifest",
    "explain_provenance",
)


def available_read_only_tools() -> list[str]:
    return list(READ_ONLY_TOOL_NAMES)


def search_context(reader: PackReader, query: str, *, limit: int = 10) -> dict[str, object]:
    terms = {term.lower() for term in query.split() if term.strip()}
    results: list[dict[str, Any]] = []
    for chunk in reader.iter_chunks():
        text_lower = chunk.text.lower()
        score = sum(1 for term in terms if term in text_lower)
        if score <= 0:
            continue
        first_ref = chunk.source_refs[0] if chunk.source_refs else None
        results.append(
            {
                "chunk_id": chunk.id,
                "text": chunk.text,
                "score": float(score),
                "source": {
                    "uri": first_ref.source_uri if first_ref else None,
                    "page": first_ref.page_start if first_ref else None,
                    "section": " / ".join(chunk.section_path),
                },
            }
        )
    results.sort(key=lambda item: float(item["score"]), reverse=True)
    return {"results": results[:limit]}


def get_chunk(reader: PackReader, chunk_id: str) -> dict[str, object] | None:
    for chunk in reader.iter_chunks():
        if chunk.id == chunk_id:
            return chunk.model_dump(mode="json", exclude_none=True)
    return None


def get_source_metadata(reader: PackReader, document_id: str) -> dict[str, object] | None:
    for document in reader.iter_documents():
        if document.id != document_id:
            continue
        return {
            "document_id": document.id,
            "title": document.title,
            "source": document.source.model_dump(mode="json", exclude_none=True),
            "language": document.language,
            "security": document.security.model_dump(mode="json", exclude_none=True),
            "lineage": document.lineage.model_dump(mode="json", exclude_none=True),
            "metadata": document.metadata,
            "block_count": len(document.blocks),
            "error_count": len(document.errors),
        }
    return None


def explain_provenance(reader: PackReader, chunk_id: str) -> dict[str, object] | None:
    chunk = get_chunk(reader, chunk_id)
    if chunk is None:
        return None
    raw_source_refs = chunk.get("source_refs", [])
    source_refs = (
        [ref for ref in raw_source_refs if isinstance(ref, dict)]
        if isinstance(raw_source_refs, list)
        else []
    )
    documents = {
        document.id: document
        for document in reader.iter_documents()
        if any(ref.get("document_id") == document.id for ref in source_refs)
    }
    return {
        "chunk_id": chunk_id,
        "section_path": chunk.get("section_path", []),
        "source_refs": source_refs,
        "documents": [
            {
                "document_id": document.id,
                "title": document.title,
                "source_uri": document.source.uri,
            }
            for document in documents.values()
        ],
    }


def get_manifest(reader: PackReader) -> dict[str, object]:
    return reader.manifest().model_dump(mode="json", exclude_none=True)
