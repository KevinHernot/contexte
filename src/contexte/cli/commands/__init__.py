"""CLI command registration."""

from __future__ import annotations

import typer

from contexte.cli.commands import (
    build,
    eval,
    export,
    inspect,
    plugins,
    probe,
    report,
    serve,
    validate,
)


def register_commands(app: typer.Typer) -> None:
    for module in (probe, build, inspect, validate, eval, export, report, serve, plugins):
        module.register(app)
