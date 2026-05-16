"""`ctx verify` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail


def register(app: typer.Typer) -> None:
    @app.command("verify")
    def verify_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        key: Annotated[Path, typer.Option("--key", help="Path to public key.")] = None,
    ) -> None:
        """[ALPHA] Verify a context pack signature."""
        console.print("[yellow]ctx verify is an alpha feature.[/yellow]")
        if not key:
            console.print("[red]Error: --key is required for verification.[/red]")
            raise typer.Exit(1)
        
        # Placeholder for actual verification logic
        console.print(f"[dim]Would verify {pack} using {key}...[/dim]")
        console.print("[red]Feature not yet implemented: requires 'cryptography' dependency.[/red]")
        raise typer.Exit(1)
