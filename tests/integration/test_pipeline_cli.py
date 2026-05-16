from __future__ import annotations

import json
import pytest
from pathlib import Path

from typer.testing import CliRunner

from conftest import FIXTURES
from contexte.cli.app import app
from contexte.core.discovery import probe_path
from contexte.core.errors import PackError
from contexte.core.pipeline import build_context_pack
from contexte.eval.report import write_eval_report
from contexte.eval.suite_basic import evaluate_pack
from contexte.exporters.jsonl import JsonlExporter
from contexte.exporters.markdown import MarkdownExporter
from contexte.mcp.tools import (
    explain_provenance,
    get_chunk,
    get_manifest,
    get_source_metadata,
    search_context,
)
from contexte.pack.reader import PackReader

runner = CliRunner()


def test_pipeline_acceptance_flow(tmp_path: Path) -> None:
    pack = tmp_path / "quickstart.ctxpack"
    chunks_jsonl = tmp_path / "chunks.jsonl"
    markdown_dir = tmp_path / "normalized"
    eval_html = tmp_path / "eval.html"

    build = build_context_pack(FIXTURES, pack, force=True, max_chars=800)
    assert build.documents
    assert build.chunks

    reader = PackReader(pack)
    assert reader.validate().valid
    eval_report = evaluate_pack(pack)
    assert eval_report.document_count == len(build.documents)
    assert eval_report.chunk_count == len(build.chunks)
    assert eval_report.rag_readiness_score <= 100

    JsonlExporter().export(reader, chunks_jsonl)
    MarkdownExporter().export(reader, markdown_dir)
    write_eval_report(eval_report, eval_html)

    first_line = json.loads(chunks_jsonl.read_text(encoding="utf-8").splitlines()[0])
    assert {"id", "text", "metadata"} <= set(first_line)
    assert list(markdown_dir.glob("doc_*.md"))
    assert "Contexte Eval Report" in eval_html.read_text(encoding="utf-8")

    search = search_context(reader, "remote work", limit=3)
    assert search["results"]
    first_chunk_id = build.chunks[0].id
    assert get_chunk(reader, first_chunk_id)
    assert get_source_metadata(reader, build.documents[0].id)
    assert explain_provenance(reader, first_chunk_id)
    assert get_manifest(reader)["pack_id"].startswith("ctxpack_")


def test_cli_commands_end_to_end(tmp_path: Path) -> None:
    pack = tmp_path / "cli.ctxpack"
    jsonl = tmp_path / "cli.jsonl"
    markdown_dir = tmp_path / "md"
    report = tmp_path / "eval.html"

    commands = [
        ["probe", str(FIXTURES), "--json"],
        ["probe", str(FIXTURES), "--quiet"],
        ["probe", str(FIXTURES), "--verbose"],
        [
            "build",
            str(FIXTURES),
            "--to",
            str(pack),
            "--report",
            "--force",
            "--max-chars",
            "900",
            "--json",
        ],
        ["build", str(FIXTURES), "--to", str(pack), "--force", "--quiet"],
        ["validate", str(pack), "--json"],
        ["validate", str(pack), "--quiet"],
        ["inspect", str(pack), "--json"],
        ["inspect", str(pack), "--quiet"],
        ["eval", str(pack), "--report", str(report), "--json"],
        ["eval", str(pack), "--quiet"],
        ["eval", str(pack), "--verbose"],
        ["export", str(pack), "--to", "jsonl", "--output", str(jsonl), "--json"],
        ["export", str(pack), "--to", "markdown", "--output", str(markdown_dir), "--quiet"],
        ["report", str(pack), "--output", str(tmp_path / "report.html"), "--json"],
        ["report", str(pack), "--output", str(tmp_path / "report_q.html"), "--quiet"],
        ["plugins", "list", "--json"],
        ["plugins", "list", "--quiet"],
    ]
    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, (command, result.stdout, result.exception)

    assert pack.exists()
    assert jsonl.exists()
    assert markdown_dir.exists()
    assert report.exists()


def test_export_redact_replaces_pii_and_secrets(tmp_path: Path) -> None:
    pack = tmp_path / "redact.ctxpack"
    jsonl = tmp_path / "redact.jsonl"
    md_dir = tmp_path / "redact_md"
    build_context_pack(FIXTURES, pack, force=True, max_chars=800)

    result_jsonl = runner.invoke(
        app,
        ["export", str(pack), "--to", "jsonl", "--output", str(jsonl), "--redact"],
    )
    result_md = runner.invoke(
        app,
        ["export", str(pack), "--to", "markdown", "--output", str(md_dir), "--redact"],
    )

    assert result_jsonl.exit_code == 0, result_jsonl.stdout
    assert result_md.exit_code == 0, result_md.stdout
    jsonl_text = jsonl.read_text(encoding="utf-8")
    md_text = "\n".join(p.read_text(encoding="utf-8") for p in md_dir.glob("doc_*.md"))

    assert "alex@example.com" not in jsonl_text
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in jsonl_text
    assert "[REDACTED:pii:email]" in jsonl_text
    assert "alex@example.com" not in md_text
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in md_text


def test_probe_path_reports_unsupported(tmp_path: Path) -> None:
    unsupported = tmp_path / "binary.bin"
    unsupported.write_bytes(b"not supported")
    result = probe_path(tmp_path)
    assert result.file_count == 1
    assert result.unsupported_file_count == 1
    assert result.warnings == ["unsupported_files_detected"]


def test_cli_serve_placeholder_is_explicit(tmp_path: Path) -> None:
    pack = tmp_path / "serve.ctxpack"
    build_context_pack(FIXTURES, pack, force=True, max_chars=800)

    result = runner.invoke(app, ["serve", str(pack), "--mcp", "--read-only"])

    assert result.exit_code == 1
    assert "v0.1 trust core" in result.output
    assert "contexte.mcp.tools" in result.output


def test_reader_rejects_unsafe_zip(tmp_path: Path) -> None:
    import zipfile

    unsafe_zip = tmp_path / "unsafe.ctxpack"
    with zipfile.ZipFile(unsafe_zip, "w") as zf:
        zf.writestr("../traversal.txt", "content")

    reader = PackReader(unsafe_zip)
    with pytest.raises(PackError, match="Malicious pack detected"):
        reader.validate()


def test_reader_rejects_oversized_zip(tmp_path: Path) -> None:
    import zipfile

    from contexte.constants import MAX_DECOMPRESSED_SIZE

    oversized_zip = tmp_path / "oversized.ctxpack"
    with zipfile.ZipFile(oversized_zip, "w") as zf:
        # Create a member that is just over the limit.
        # zipfile.writestr will write it even if it's large.
        zf.writestr("huge.txt", b" " * (MAX_DECOMPRESSED_SIZE + 1))

    reader = PackReader(oversized_zip)
    with pytest.raises(PackError, match="Pack exceeds maximum allowed size"):
        reader.validate()


def test_build_post_validation_fails_on_tamper(tmp_path: Path, monkeypatch) -> None:
    from contexte.core import pipeline

    # Monkeypatch the write_pack import in pipeline.py
    def broken_write_pack(*args, **kwargs):
        path = args[0]
        import zipfile

        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("garbage.txt", "not a pack")
        from contexte.pack.manifest import PackManifest

        return PackManifest.model_construct(pack_id="fake")

    monkeypatch.setattr(pipeline, "write_pack", broken_write_pack)

    with pytest.raises(PackError, match="Post-build validation failed"):
        build_context_pack(FIXTURES, tmp_path / "fail.ctxpack", force=True)


def test_validate_strict_fails_on_warnings(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "file1.txt").write_text("content")
    (input_dir / "file2.txt").write_text("content")  # Trigger exact_duplicate_source warning

    pack = tmp_path / "warn.ctxpack"
    build_context_pack(input_dir, pack, force=True)

    # Normal validate passes
    result = runner.invoke(app, ["validate", str(pack)])
    assert result.exit_code == 0

    # Strict validate fails because of warnings
    result_strict = runner.invoke(app, ["validate", str(pack), "--strict"])
    assert result_strict.exit_code == 1
    assert "Validation failed due to --strict mode" in result_strict.output


def test_build_is_network_free(tmp_path: Path, monkeypatch) -> None:
    import socket

    def forbidden(*args, **kwargs):
        raise RuntimeError("Network access is forbidden in Contexte core.")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "bind", forbidden)

    pack = tmp_path / "offline.ctxpack"
    # Should complete without raising RuntimeError from socket
    build_context_pack(FIXTURES, pack, force=True)
    assert pack.exists()

def test_eval_reference_calculates_recall(tmp_path: Path) -> None:
    from typer.testing import CliRunner
    from contexte.cli.app import app
    from contexte.core.pipeline import build_context_pack
    runner = CliRunner()
    
    ref_dir = tmp_path / "ref"
    ref_dir.mkdir()
    (ref_dir / "doc1.txt").write_text("content1")
    (ref_dir / "doc2.txt").write_text("content2")

    ref_pack = tmp_path / "reference.ctxpack"
    build_context_pack(ref_dir, ref_pack, force=True)

    curr_dir = tmp_path / "curr"
    curr_dir.mkdir()
    (curr_dir / "doc1.txt").write_text("content1")  # doc2 is missing

    curr_pack = tmp_path / "current.ctxpack"
    build_context_pack(curr_dir, curr_pack, force=True)

    result = runner.invoke(app, ["eval", str(curr_pack), "--reference", str(ref_pack), "--verbose"])
    assert result.exit_code == 0
    assert "document recall 50.0%" in result.output
    assert "missing 1 docs from reference" in result.output
