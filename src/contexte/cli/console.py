"""CLI console helpers."""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from contexte.core.errors import ContexteError
from contexte.ir.serialize import to_jsonable

console = Console()
err_console = Console(stderr=True)


def print_json(value: Any) -> None:
    print(json.dumps(to_jsonable(value), ensure_ascii=False, sort_keys=True, indent=2))


def fail(error: Exception) -> None:
    message = str(error)
    if isinstance(error, ContexteError):
        err_console.print(f"[red]Error:[/red] {message}")
    else:
        err_console.print(f"[red]Unexpected error:[/red] {message}")
    raise typer.Exit(1)


def summary_table(title: str, rows: list[tuple[str, object]]) -> Table:
    table = Table(title=title, show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for key, value in rows:
        table.add_row(key, str(value))
    return table
