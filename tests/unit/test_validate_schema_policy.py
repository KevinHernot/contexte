from __future__ import annotations

from datetime import UTC, datetime

from contexte.ir.models import (
    Block,
    ChunkSourceRef,
    ContextChunk,
    ContextDocument,
    Lineage,
    SecurityFinding,
    SourceRef,
    SourceSpan,
)
from contexte.ir.schema import json_schemas
from contexte.ir.validate import validate_chunk, validate_document, validate_manifest
from contexte.pack.manifest import PackFeatures, PackManifest, SourceSummary
from contexte.security.policy import has_blocking_findings


def _document(*, blocks: list[Block] | None = None) -> ContextDocument:
    return ContextDocument(
        id="doc_1234567890abcdef",
        source=SourceRef(uri="file:///tmp/sample.txt", type="file", media_type="text/plain"),
        extracted_at=datetime.now(tz=UTC),
        blocks=blocks
        if blocks is not None
        else [Block(id="blk_1234567890abcdef_000000", type="paragraph", text="hello")],
        lineage=Lineage(decoder="text", pipeline_version="0.1.0", pipeline_config_hash="abc"),
    )


def test_validate_document_flags_missing_id_prefix_and_blocks() -> None:
    bad = _document(blocks=[])
    bad.id = "wrong_prefix"
    bad.source.uri = ""

    errors = validate_document(bad)

    assert any("id must start with doc_" in error for error in errors)
    assert any("source.uri is required" in error for error in errors)
    assert any("no blocks" in error for error in errors)


def test_validate_document_clean_returns_empty() -> None:
    assert validate_document(_document()) == []


def test_validate_chunk_catches_id_and_text_problems() -> None:
    chunk = ContextChunk(
        id="bad_id",
        document_id="doc_1234567890abcdef",
        text="   ",
        source_refs=[],
        char_count=0,
    )

    errors = validate_chunk(chunk)

    assert any("must start with chk_" in error for error in errors)
    assert any("text is empty" in error for error in errors)
    assert any("source_refs is empty" in error for error in errors)


def test_validate_chunk_char_count_mismatch() -> None:
    chunk = ContextChunk(
        id="chk_1234567890abcdef_heading_000000",
        document_id="doc_1234567890abcdef",
        text="abc",
        source_refs=[
            ChunkSourceRef(
                document_id="doc_1234567890abcdef",
                block_ids=["blk_1234567890abcdef_000000"],
                source_uri="file:///tmp/x.txt",
            )
        ],
        char_count=999,
    )

    errors = validate_chunk(chunk)

    assert any("char_count mismatch" in error for error in errors)


def test_validate_manifest_requires_pack_id_prefix_and_features() -> None:
    bad = PackManifest(
        pack_id="missing_prefix",
        created_at=datetime.now(tz=UTC),
        source_summary=SourceSummary(source_root="/tmp", document_count=0, chunk_count=0),
        features=PackFeatures(has_documents=False, has_chunks=False),
    )

    errors = validate_manifest(bad)

    assert any("pack_id must start with ctxpack_" in error for error in errors)
    assert any("has_documents" in error for error in errors)
    assert any("has_chunks" in error for error in errors)


def test_json_schemas_returns_public_models() -> None:
    schemas = json_schemas()

    assert {"ContextDocument", "ContextChunk", "SecurityFinding", "PackManifest"} <= schemas.keys()
    for value in schemas.values():
        assert isinstance(value, dict)


def test_v01_policy_never_blocks() -> None:
    finding = SecurityFinding(
        id="fnd_x",
        document_id="doc_1234567890abcdef",
        type="secret",
        label="secret:api_key",
        severity="high",
        location=SourceSpan(start=0, end=4),
    )

    assert has_blocking_findings([finding]) is False
    assert has_blocking_findings([]) is False
