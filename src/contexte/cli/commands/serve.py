"""`ctx serve` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer

from contexte.cli.console import fail
from contexte.mcp.server import serve_adapter_placeholder


def register(app: typer.Typer) -> None:
    @app.command("serve")
    def serve_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        mcp: Annotated[
            bool, typer.Option("--mcp", help="Future experimental MCP adapter (read-only only).")
        ] = False,
        http: Annotated[
            bool, typer.Option("--http", help="Future local HTTP adapter (read-only only).")
        ] = False,
        read_only: Annotated[
            bool,
            typer.Option(
                "--read-only/--allow-write",
                help="Reserved for future serving adapters. Read-only is the default and only supported mode in v0.1.",
            ),
        ] = True,
        port: Annotated[int, typer.Option("--port", help="Port for future server modes.")] = 8787,
    ) -> None:
        try:
            if mcp == http:
                raise typer.BadParameter(
                    "Choose exactly one of --mcp or --http. Serving is optional and placeholder-only in v0.1."
                )
            mode: Literal["mcp", "http"] = "mcp" if mcp else "http"
            serve_adapter_placeholder(pack, mode=mode, port=port, read_only=read_only)
        except Exception as exc:
            fail(exc)
