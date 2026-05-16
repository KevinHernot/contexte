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
        """Verify a context pack signature using a public Ed25519 key."""
        from contexte.pack.reader import PackReader

        if not key:
            fail(ValueError("--key is required for verification."))

        try:
            reader = PackReader(pack, public_key_path=key)
            result = reader.validate()
            if result.valid:
                console.print(f"[green]✓ Signature and integrity verified for {pack}[/green]")
            else:
                console.print(f"[red]✗ Verification failed for {pack}[/red]")
                for err in result.errors:
                    console.print(f"  - {err}")
                raise typer.Exit(1)
        except Exception as exc:
            fail(exc)
