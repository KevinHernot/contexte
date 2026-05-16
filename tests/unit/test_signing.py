import pytest
from pathlib import Path
from datetime import datetime, UTC
from contexte.core.signing import generate_key_pair, sign_data, verify_signature
from contexte.pack.writer import write_pack
from contexte.pack.reader import PackReader
from contexte.ir.models import BuildReport, ContextChunk, ContextDocument, SecurityFinding

def test_sign_and_verify(tmp_path):
    keys_dir = tmp_path / "keys"
    priv, pub = generate_key_pair(keys_dir)
    
    pack_path = tmp_path / "test.ctxpack"
    doc = ContextDocument(
        id="doc_1",
        title="Test",
        source={"type": "file", "uri": "file://test.md", "sha256": "abc", "size_bytes": 10},
        blocks=[{"id": "b1", "type": "paragraph", "text": "hello"}],
        extracted_at=datetime.now(UTC),
        lineage={
            "created_by": "test",
            "pipeline_version": "0.1.0",
            "decoder": "markdown",
            "pipeline_config_hash": "abc"
        }
    )
    
    # Write signed pack
    write_pack(
        pack_path,
        source_root=".",
        documents=[doc],
        chunks=[],
        findings=[],
        build_report=BuildReport(
            warnings=[], 
            security_finding_count=0,
            created_at=datetime.now(UTC),
            chunk_count=0,
            document_count=1,
            unsupported_file_count=0,
            failed_file_count=0,
            discovered_file_count=1,
            supported_file_count=1,
            source_root="."
        ),
        pipeline_config={},
        private_key_path=priv
    )
    
    # Verify with correct key
    reader = PackReader(pack_path, public_key_path=pub)
    result = reader.validate()
    assert result.valid
    
    # Verify with wrong key
    _, other_pub = generate_key_pair(tmp_path / "other_keys", name="other")
    reader_wrong = PackReader(pack_path, public_key_path=other_pub)
    result_wrong = reader_wrong.validate()
    assert not result_wrong.valid
    assert "signature verification failed" in result_wrong.errors[0].lower()

def test_unsigned_pack_with_key(tmp_path):
    pack_path = tmp_path / "unsigned.ctxpack"
    doc = ContextDocument(
        id="doc_1",
        title="Test",
        source={"type": "file", "uri": "file://test.md", "sha256": "abc", "size_bytes": 10},
        blocks=[{"id": "b1", "type": "paragraph", "text": "hello"}],
        extracted_at=datetime.now(UTC),
        lineage={
            "created_by": "test",
            "pipeline_version": "0.1.0",
            "decoder": "markdown",
            "pipeline_config_hash": "abc"
        }
    )
    write_pack(
        pack_path,
        source_root=".",
        documents=[doc],
        chunks=[],
        findings=[],
        build_report=BuildReport(
            warnings=[], 
            security_finding_count=0,
            created_at=datetime.now(UTC),
            chunk_count=0,
            document_count=1,
            unsupported_file_count=0,
            failed_file_count=0,
            discovered_file_count=1,
            supported_file_count=1,
            source_root="."
        ),
        pipeline_config={}
    )
    
    _, pub = generate_key_pair(tmp_path / "keys")
    reader = PackReader(pack_path, public_key_path=pub)
    result = reader.validate()
    assert not result.valid
    assert "pack is not signed" in result.errors[0].lower()
