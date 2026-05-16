"""`ctx probe` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json, summary_table
from contexte.core.pipeline import probe


def register(app: typer.Typer) -> None:
    @app.command("probe")
    def probe_cmd(
        path: Annotated[Path, typer.Argument(help="File or directory to inspect.")],
        config: Annotated[
            Path | None, typer.Option("--config", help="Optional contexte.yaml/json config.")
        ] = None,
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        verbose: Annotated[bool, typer.Option("--verbose", help="Show file lists.")] = False,
        explain: Annotated[
            bool, typer.Option("--explain", help="Show support explanation per file.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        try:
            result = probe(path, config_path=config)
        except Exception as exc:
            fail(exc)
        if json_output:
            print_json(result)
            return
        if result.exists is False:
            console.print(f"[red]Path does not exist:[/red] {path}")
            raise typer.Exit(1)
        if not quiet:
            console.print(
                summary_table(
                    "Contexte Probe",
                    [
                        ("Path", result.path),
                        ("Files", result.file_count),
                        ("Supported", result.supported_file_count),
                        ("Unsupported", result.unsupported_file_count),
                        ("Total size", f"{result.total_size_bytes:,} bytes"),
                        (
                            "Types",
                            ", ".join(f"{k}:{v}" for k, v in result.file_types.items()) or "none",
                        ),
                    ],
                )
            )
            if verbose or explain:
                for item in result.supported_files:
                    explanation = f" ({result.explanations.get(item)})" if explain else ""
                    console.print(f"[green]supported[/green] {item}{explanation}")
                for item in result.unsupported_files:
                    explanation = f" ({result.explanations.get(item)})" if explain else ""
                    console.print(f"[yellow]unsupported[/yellow] {item}{explanation}")
