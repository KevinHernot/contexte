"""`ctx eval` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail, print_json, summary_table
from contexte.eval.report import write_eval_report
from contexte.eval.suite_basic import evaluate_pack


def register(app: typer.Typer) -> None:
    @app.command("eval")
    def eval_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        suite: Annotated[str, typer.Option("--suite", help="Eval suite to run.")] = "basic",
        report: Annotated[
            Path | None, typer.Option("--report", help="Write eval report (.html or .json).")
        ] = None,
        reference: Annotated[
            Path | None, typer.Option("--reference", help="Golden .ctxpack to compare against.")
        ] = None,
        json_output: Annotated[
            bool, typer.Option("--json", help="Print machine-readable JSON.")
        ] = False,
        verbose: Annotated[bool, typer.Option("--verbose", help="Show score explanation.")] = False,
        quiet: Annotated[bool, typer.Option("--quiet", help="Suppress human output.")] = False,
    ) -> None:
        if suite != "basic":
            console.print("[red]Only the basic suite is available in v0.1.[/red]")
            raise typer.Exit(1)
        try:
            result = evaluate_pack(pack, reference_path=reference)
            if report:
                write_eval_report(result, report)
        except Exception as exc:
            fail(exc)
        if json_output:
            print_json(result)
            return
        if not quiet:
            console.print(
                summary_table(
                    "Contexte Eval",
                    [
                        ("RAG readiness score", f"{result.rag_readiness_score}/100"),
                        ("Documents", result.document_count),
                        ("Chunks", result.chunk_count),
                        ("Average chunk length", f"{result.avg_chunk_chars:,.0f} chars"),
                        ("Chunks without citations", result.chunks_without_source_refs),
                        ("PII findings", result.pii_finding_count),
                        ("Secret findings", result.secret_finding_count),
                        ("Prompt injection warnings", result.prompt_injection_finding_count),
                    ],
                )
            )
            console.print(
                "[dim]This score is a heuristic quality signal, not a guarantee of RAG performance.[/dim]"
            )
            if verbose:
                console.print("\n[bold]Score Explanation:[/bold]")
                for line in result.score_explanation:
                    console.print(line)
                
                if result.plugin_metrics:
                    console.print("\n[bold]Plugin Metrics:[/bold]")
                    for metric_id, value in result.plugin_metrics.items():
                        console.print(f"  [cyan]{metric_id}:[/cyan] {value}")
            if report:
                console.print(f"[green]Report:[/green] {report}")
