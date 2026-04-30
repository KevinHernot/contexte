"""`ctx plugins` commands."""

from __future__ import annotations

import typer

from contexte.cli.console import console, print_json, summary_table
from contexte.plugins.loader import load_plugins

plugins_app = typer.Typer(help="Inspect optional Contexte plugins.", no_args_is_help=True)


@plugins_app.command("list")
def list_plugins(
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    registry = load_plugins()
    payload = {
        "decoders": [getattr(item, "id", repr(item)) for item in registry.decoders],
        "chunkers": [getattr(item, "id", repr(item)) for item in registry.chunkers],
        "exporters": [getattr(item, "id", repr(item)) for item in registry.exporters],
        "eval_suites": [getattr(item, "id", repr(item)) for item in registry.eval_suites],
    }
    if json_output:
        print_json(payload)
        return
    console.print(
        summary_table(
            "Contexte Plugins",
            [
                (key.replace("_", " ").title(), ", ".join(values) or "none")
                for key, values in payload.items()
            ],
        )
    )


def register(app: typer.Typer) -> None:
    app.add_typer(plugins_app, name="plugins")
