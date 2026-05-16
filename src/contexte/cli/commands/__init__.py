"""CLI command registration."""

from __future__ import annotations

import typer

from contexte.cli.commands import (
    build,
    diff,
    eval,
    export,
    inspect,
    plugins,
    probe,
    report,
    schemas,
    serve,
    sign,
    validate,
    verify,
)


def register_commands(app: typer.Typer) -> None:
    for module in (probe, build, inspect, validate, diff, eval, export, report, schemas, serve, sign, verify, plugins):
        module.register(app)
