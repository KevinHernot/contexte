"""`ctx export` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json
from contexte.exporters.jsonl import JsonlExporter
from contexte.exporters.langchain import LangChainExporter
from contexte.exporters.llamaindex import LlamaIndexExporter
from contexte.exporters.markdown import MarkdownExporter
from contexte.pack.reader import PackReader


def register(app: typer.Typer) -> None:
    @app.command("export")
    def export_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        to: Annotated[str, typer.Option("--to", help="Export format: jsonl, markdown, langchain, or llamaindex.")],
        output: Annotated[Path, typer.Option("--output", help="Output file or directory.")],
        redact: Annotated[
            bool,
            typer.Option(
                "--redact",
                help="Replace PII and secret findings with [REDACTED:label] placeholders.",
            ),
        ] = False,
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        try:
            reader = PackReader(pack)
            if to == "jsonl":
                JsonlExporter(redact=redact).export(reader, output)
            elif to == "markdown":
                MarkdownExporter(redact=redact).export(reader, output)
            elif to == "langchain":
                LangChainExporter(redact=redact).export(reader, output)
            elif to == "llamaindex":
                LlamaIndexExporter(redact=redact).export(reader, output)
            else:
                console.print("[red]Unsupported export format. Use jsonl, markdown, langchain, or llamaindex.[/red]")
                raise typer.Exit(1)
        except Exception as exc:
            fail(exc)
        if json_output:
            print_json({"pack": str(pack), "format": to, "output": str(output), "redacted": redact})
            return
        if not quiet:
            redact_note = " (redacted)" if redact else ""
            console.print(f"[green]Exported[/green] {pack} -> {output} ({to}){redact_note}")
