from __future__ import annotations

from pathlib import Path

import pytest

from conftest import FIXTURES
from contexte.core.errors import PackError
from contexte.core.pipeline import build_context_pack
from contexte.pack.reader import PackReader


def test_pack_writer_reader_and_validation(tmp_path: Path) -> None:
    output = tmp_path / "fixture.ctxpack"
    result = build_context_pack(FIXTURES, output, force=True, max_chars=500)

    assert output.exists()
    assert result.manifest.source_summary.document_count >= 7
    assert result.manifest.source_summary.chunk_count >= 7

    reader = PackReader(output)
    validation = reader.validate()
    assert validation.valid, validation.errors
    assert reader.manifest().pack_id.startswith("ctxpack_")
    assert len(list(reader.iter_documents())) == result.manifest.source_summary.document_count
    assert len(list(reader.iter_chunks())) == result.manifest.source_summary.chunk_count
    assert len(list(reader.iter_findings())) >= 3


def test_pack_writer_refuses_overwrite_without_force(tmp_path: Path) -> None:
    output = tmp_path / "fixture.ctxpack"
    build_context_pack(FIXTURES / "simple.txt", output, force=True)
    with pytest.raises(PackError):
        build_context_pack(FIXTURES / "simple.txt", output, force=False)


def test_pack_validation_reports_missing_pack(tmp_path: Path) -> None:
    result = PackReader(tmp_path / "missing.ctxpack").validate()
    assert not result.valid
    assert result.errors
