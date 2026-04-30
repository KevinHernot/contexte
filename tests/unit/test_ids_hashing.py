from __future__ import annotations

from pathlib import Path

from contexte.core.hashing import checksum_for_file, sha256_file, sha256_text, stable_json_hash
from contexte.core.ids import (
    block_id,
    chunk_id,
    document_id,
    finding_id,
    normalize_uri_for_id,
    pack_id,
)


def test_hashing_and_ids_are_stable(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")

    assert sha256_text("hello") == sha256_file(file_path)
    assert checksum_for_file(file_path).startswith("sha256:")
    assert stable_json_hash({"b": 2, "a": 1}) == stable_json_hash({"a": 1, "b": 2})

    doc_id = document_id(sha256_file(file_path), file_path.resolve().as_uri())
    assert doc_id.startswith("doc_")
    assert block_id(doc_id, 7).startswith("blk_")
    assert chunk_id(doc_id, "heading", 2).startswith("chk_")
    assert finding_id(doc_id, "pii:email", 0).startswith("fnd_")
    assert pack_id("abcdef1234567890").startswith("ctxpack_")
    assert normalize_uri_for_id("file:///A Path/Doc.md") == "file_a_path_doc_md"
