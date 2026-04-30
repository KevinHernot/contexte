"""`ctx inspect` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json, summary_table
from contexte.pack.reader import PackReader


def register(app: typer.Typer) -> None:
    @app.command("inspect")
    def inspect_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        try:
            reader = PackReader(pack)
            manifest = reader.manifest()
            build_report = reader.build_report()
            findings_count = sum(1 for _ in reader.iter_findings())
            payload = {
                "path": str(pack),
                "manifest": manifest,
                "security_findings": findings_count,
                "build_warnings": len(build_report.warnings),
            }
        except Exception as exc:
            fail(exc)
        if json_output:
            print_json(payload)
            return
        if not quiet:
            console.print(
                summary_table(
                    "Contexte Pack",
                    [
                        ("Path", pack),
                        ("Schema", manifest.schema_version),
                        ("Documents", manifest.source_summary.document_count),
                        ("Chunks", manifest.source_summary.chunk_count),
                        ("Security findings", findings_count),
                        ("Build warnings", len(build_report.warnings)),
                        ("Eval available", manifest.features.has_eval),
                    ],
                )
            )
