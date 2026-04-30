"""Main `ctx` CLI entrypoint."""

from __future__ import annotations

import typer

from contexte import __version__
from contexte.cli.commands import register_commands

app = typer.Typer(
    name="ctx",
    help="Compile raw documents into trustworthy, portable AI context packs.",
    no_args_is_help=True,
)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show Contexte version and exit."),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()


register_commands(app)


if __name__ == "__main__":
    app()
