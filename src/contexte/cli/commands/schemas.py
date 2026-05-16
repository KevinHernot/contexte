"""`ctx schemas` command."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from contexte.cli.console import console
from contexte.ir.models import ContextChunk, ContextDocument
from contexte.pack.manifest import PackManifest


def register(app: typer.Typer) -> None:
    @app.command("schemas")
    def schemas_cmd(
        model: Annotated[
            str,
            typer.Option(
                "--model",
                help="Model to export: document, chunk, or manifest. Default is all.",
            ),
        ] = "all",
    ) -> None:
        """Export JSON schemas for Context IR and Pack formats."""
        schemas = {
            "document": ContextDocument.model_json_schema(),
            "chunk": ContextChunk.model_json_schema(),
            "manifest": PackManifest.model_json_schema(),
        }

        if model == "all":
            console.print(json.dumps(schemas, indent=2))
        elif model in schemas:
            console.print(json.dumps(schemas[model], indent=2))
        else:
            console.print(f"[red]Error: Unknown model '{model}'. Valid models: {', '.join(schemas.keys())}[/red]")
            raise typer.Exit(1)
