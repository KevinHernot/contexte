"""`ctx report` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json
from contexte.eval.report import write_eval_report
from contexte.eval.suite_basic import evaluate_pack


def register(app: typer.Typer) -> None:
    @app.command("report")
    def report_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        output: Annotated[
            Path, typer.Option("--output", help="Output .html or .json report path.")
        ],
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        try:
            result = evaluate_pack(pack)
            write_eval_report(result, output)
        except Exception as exc:
            fail(exc)
        if json_output:
            print_json({"pack": str(pack), "output": str(output), "eval": result})
            return
        if not quiet:
            console.print(f"[green]Report written:[/green] {output}")
