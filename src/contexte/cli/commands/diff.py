"""`ctx diff` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json, summary_table
from contexte.pack.reader import PackReader


def register(app: typer.Typer) -> None:
    @app.command("diff")
    def diff_cmd(
        old: Annotated[Path, typer.Argument(help="Original .ctxpack path.")],
        new: Annotated[Path, typer.Argument(help="New .ctxpack path.")],
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        """Compare two context packs."""
        try:
            reader_old = PackReader(old)
            reader_new = PackReader(new)

            m_old = reader_old.manifest()
            m_new = reader_new.manifest()

            br_old = reader_old.build_report()
            br_new = reader_new.build_report()

            # For findings, we'll just count them for now in v0.1
            findings_old = sum(1 for _ in reader_old.iter_findings())
            findings_new = sum(1 for _ in reader_new.iter_findings())

            diff = {
                "old_path": str(old),
                "new_path": str(new),
                "schema": {
                    "old": m_old.schema_version,
                    "new": m_new.schema_version,
                    "changed": m_old.schema_version != m_new.schema_version,
                },
                "counts": {
                    "documents": {
                        "old": m_old.source_summary.document_count,
                        "new": m_new.source_summary.document_count,
                        "diff": m_new.source_summary.document_count - m_old.source_summary.document_count,
                    },
                    "chunks": {
                        "old": m_old.source_summary.chunk_count,
                        "new": m_new.source_summary.chunk_count,
                        "diff": m_new.source_summary.chunk_count - m_old.source_summary.chunk_count,
                    },
                    "security_findings": {
                        "old": findings_old,
                        "new": findings_new,
                        "diff": findings_new - findings_old,
                    },
                },
                "build": {
                    "warnings": {
                        "old": len(br_old.warnings),
                        "new": len(br_new.warnings),
                        "diff": len(br_new.warnings) - len(br_old.warnings),
                    },
                    "errors": {
                        "old": len(br_old.errors),
                        "new": len(br_new.errors),
                        "diff": len(br_new.errors) - len(br_old.errors),
                    },
                },
            }

        except Exception as exc:
            fail(exc)

        if json_output:
            print_json(diff)
            return

        if not quiet:
            rows = [
                ("Documents", f"{diff['counts']['documents']['old']} -> {diff['counts']['documents']['new']} ({diff['counts']['documents']['diff']:+})"),
                ("Chunks", f"{diff['counts']['chunks']['old']} -> {diff['counts']['chunks']['new']} ({diff['counts']['chunks']['diff']:+})"),
                ("Security findings", f"{diff['counts']['security_findings']['old']} -> {diff['counts']['security_findings']['new']} ({diff['counts']['security_findings']['diff']:+})"),
                ("Build warnings", f"{diff['build']['warnings']['old']} -> {diff['build']['warnings']['new']} ({diff['build']['warnings']['diff']:+})"),
                ("Build errors", f"{diff['build']['errors']['old']} -> {diff['build']['errors']['new']} ({diff['build']['errors']['diff']:+})"),
            ]
            if diff["schema"]["changed"]:
                rows.insert(0, ("Schema version", f"{diff['schema']['old']} -> {diff['schema']['new']} (CHANGED)"))
            
            console.print(summary_table("Contexte Pack Diff", rows))
