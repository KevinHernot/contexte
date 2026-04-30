from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from conftest import FIXTURES
from contexte.cli.app import app
from contexte.core.discovery import probe_path
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
        ["validate", str(pack), "--json"],
        ["inspect", str(pack), "--json"],
        ["eval", str(pack), "--report", str(report), "--json"],
        ["export", str(pack), "--to", "jsonl", "--output", str(jsonl), "--json"],
        ["export", str(pack), "--to", "markdown", "--output", str(markdown_dir), "--json"],
        ["report", str(pack), "--output", str(tmp_path / "report.html"), "--json"],
        ["plugins", "list", "--json"],
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
