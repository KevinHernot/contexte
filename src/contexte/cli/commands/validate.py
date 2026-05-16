"""`ctx validate` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, print_json, summary_table
from contexte.pack.reader import PackReader


def register(app: typer.Typer) -> None:
    @app.command("validate")
    def validate_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        skip_checksums: Annotated[
            bool, typer.Option("--skip-checksums", help="Do not validate member checksums.")
        ] = False,
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        strict: Annotated[
            bool, typer.Option("--strict", help="Fail on warnings as well as errors.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        result = PackReader(pack, skip_checksums=skip_checksums).validate()
        if json_output:
            print_json(result)
            if not result.valid or (strict and result.warnings):
                raise typer.Exit(1)
            return
        if not quiet:
            console.print(
                summary_table(
                    "Contexte Validation",
                    [
                        ("Path", pack),
                        ("Valid", result.valid),
                        ("Errors", len(result.errors)),
                        ("Warnings", len(result.warnings)),
                    ],
                )
            )
            for error in result.errors:
                console.print(f"[red]error[/red] {error}")
            for warning in result.warnings:
                console.print(f"[yellow]warning[/yellow] {warning}")
        if not result.valid or (strict and result.warnings):
            if strict and result.warnings and result.valid:
                console.print("[red]Validation failed due to --strict mode (warnings found).[/red]")
            raise typer.Exit(1)
