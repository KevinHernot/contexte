"""`ctx build` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json, summary_table
from contexte.core.pipeline import build_context_pack
from contexte.eval.report import write_build_report


def register(app: typer.Typer) -> None:
    @app.command("build")
    def build_cmd(
        path: Annotated[Path, typer.Argument(help="Input file or directory to compile.")],
        to: Annotated[Path, typer.Option("--to", help="Output .ctxpack path.")],
        config: Annotated[
            Path | None, typer.Option("--config", help="Optional contexte.yaml/json config.")
        ] = None,
        chunker: Annotated[
            str, typer.Option("--chunker", help="Chunker: heading, fixed, or semantic.")
        ] = "heading",
        max_chars: Annotated[
            int, typer.Option("--max-chars", help="Maximum characters per chunk.")
        ] = 3000,
        include: Annotated[
            list[str] | None, typer.Option("--include", help="Glob to include; can be repeated.")
        ] = None,
        exclude: Annotated[
            list[str] | None, typer.Option("--exclude", help="Glob to exclude; can be repeated.")
        ] = None,
        report: Annotated[
            bool, typer.Option("--report", help="Write an adjacent HTML build report.")
        ] = False,
        force: Annotated[bool, typer.Option("--force", help="Overwrite existing output.")] = False,
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        try:
            result = build_context_pack(
                path,
                to,
                config_path=config,
                include=include,
                exclude=exclude,
                chunker=chunker,
                max_chars=max_chars,
                force=force,
            )
            report_path = None
            if report:
                report_path = to.with_suffix(".report.html")
                write_build_report(result.build_report, report_path)
        except Exception as exc:
            fail(exc)
        if json_output:
            print_json(
                {
                    "output": str(result.output),
                    "manifest": result.manifest,
                    "build_report": result.build_report,
                    "report": str(report_path) if report_path else None,
                }
            )
            return
        if not quiet:
            console.print(
                summary_table(
                    "Contexte Build",
                    [
                        ("Output", result.output),
                        ("Pack ID", result.manifest.pack_id),
                        ("Documents", result.manifest.source_summary.document_count),
                        ("Chunks", result.manifest.source_summary.chunk_count),
                        ("Security findings", result.build_report.security_finding_count),
                        ("Warnings", len(result.build_report.warnings)),
                    ],
                )
            )
            if report_path:
                console.print(f"[green]Report:[/green] {report_path}")
