from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from conftest import FIXTURES
from contexte.chunkers.base import ChunkerConfig
from contexte.chunkers.fixed import FixedChunker
from contexte.chunkers.heading import HeadingChunker
from contexte.core.hashing import sha256_file, stable_json_hash
from contexte.core.ids import document_id
from contexte.decoders.base import DecodeContext
from contexte.decoders.registry import default_registry
from contexte.ir.models import ContextDocument
from contexte.normalizers.metadata import source_ref_for_path


def _decode(path: Path) -> ContextDocument:
    source_hash = sha256_file(path)
    source_ref = source_ref_for_path(path, sha256=source_hash, root=FIXTURES)
    context = DecodeContext(
        source_root=FIXTURES,
        document_id=document_id(source_hash, source_ref.uri),
        source_ref=source_ref,
        pipeline_config_hash=stable_json_hash({"test": True}),
        extracted_at=datetime.now(tz=UTC),
    )
    decoder = default_registry().decoder_for(source_ref)
    assert decoder is not None
    return decoder.decode(path, context)


def test_required_decoders_extract_blocks() -> None:
    for filename in [
        "simple.md",
        "simple.txt",
        "simple.html",
        "simple.pdf",
        "simple.docx",
        "table.csv",
        "data.json",
    ]:
        document = _decode(FIXTURES / filename)
        assert document.id.startswith("doc_")
        assert document.blocks, filename
        assert document.source.original_path == filename


def test_heading_chunker_preserves_section_path() -> None:
    document = _decode(FIXTURES / "simple.md")
    chunks = HeadingChunker(ChunkerConfig(max_chars=120, overlap_chars=20)).chunk(document)
    assert chunks
    assert all(chunk.source_refs for chunk in chunks)
    assert any("Remote Work" in chunk.section_path for chunk in chunks)
    assert all(chunk.quality.has_citation for chunk in chunks)


def test_fixed_chunker_splits_large_text() -> None:
    document = _decode(FIXTURES / "simple.txt")
    document.blocks[0].text = "alpha " * 200
    chunks = FixedChunker(ChunkerConfig(max_chars=80, overlap_chars=10)).chunk(document)
    assert len(chunks) > 1
    assert all(chunk.char_count <= 80 for chunk in chunks)
