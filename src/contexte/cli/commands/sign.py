"""`ctx sign` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail


def register(app: typer.Typer) -> None:
    @app.command("sign")
    def sign_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        key: Annotated[Path, typer.Option("--key", help="Path to private key.")] = None,
    ) -> None:
        """[ALPHA] Sign a context pack manifest."""
        console.print("[yellow]ctx sign is an alpha feature.[/yellow]")
        if not key:
            console.print("[red]Error: --key is required for signing.[/red]")
            raise typer.Exit(1)
        
        # Placeholder for actual signing logic
        console.print(f"[dim]Would sign {pack} using {key}...[/dim]")
        console.print("[red]Feature not yet implemented: requires 'cryptography' dependency.[/red]")
        raise typer.Exit(1)
