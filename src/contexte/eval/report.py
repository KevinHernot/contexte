"""HTML report rendering."""

from __future__ import annotations

import html
from pathlib import Path

from contexte.ir.models import BasicEvalReport, BuildReport
from contexte.ir.serialize import dumps_json, write_json


def write_eval_report(report: BasicEvalReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".json":
        write_json(output, report, pretty=True)
    else:
        output.write_text(render_eval_html(report), encoding="utf-8")


def render_eval_html(report: BasicEvalReport) -> str:
    warning_items = "".join(f"<li>{html.escape(warning)}</li>" for warning in report.warnings[:50])
    explanation_items = "".join(
        f"<li>{html.escape(item)}</li>" for item in report.score_explanation
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Contexte Eval Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem; color: #172033; background: #f7f8fb; }}
    main {{ max-width: 980px; margin: auto; background: white; border: 1px solid #e5e7ef; border-radius: 18px; padding: 2rem; box-shadow: 0 16px 40px rgba(31, 42, 68, .08); }}
    h1, h2 {{ color: #111827; }}
    .score {{ font-size: 3rem; font-weight: 800; color: #2563eb; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; }}
    .card {{ background: #f9fafb; border: 1px solid #edf0f7; border-radius: 14px; padding: 1rem; }}
    .label {{ color: #6b7280; font-size: .85rem; }}
    .value {{ font-size: 1.5rem; font-weight: 700; margin-top: .25rem; }}
    pre {{ background: #111827; color: #e5e7eb; padding: 1rem; border-radius: 12px; overflow: auto; }}
  </style>
</head>
<body>
<main>
  <h1>Contexte Eval Report</h1>
  <section>
    <div class=\"label\">RAG readiness score</div>
    <div class=\"score\">{report.rag_readiness_score}/100</div>
    <p>This score is a practical heuristic for triage, not a scientific benchmark.</p>
  </section>
  <h2>Executive summary</h2>
  <div class=\"grid\">
    <p>This score is a practical heuristic for triage, not a scientific benchmark and not a guarantee of RAG performance.</p>
    {_metric("Chunks", report.chunk_count)}
    {_metric("Average chunk chars", f"{report.avg_chunk_chars:,.0f}")}
    {_metric("Chunks without citations", f"{report.chunks_without_citations_ratio:.1%}")}
    {_metric("PII findings", report.pii_finding_count)}
    {_metric("Secret findings", report.secret_finding_count)}
    {_metric("Prompt injection warnings", report.prompt_injection_finding_count)}
    {_metric("Duplicate chunk ratio", f"{report.duplicate_chunk_ratio:.1%}")}
  </div>
  <h2>Score explanation</h2>
  <ul>{explanation_items}</ul>
  <h2>Top warnings</h2>
  <ul>{warning_items or "<li>No warnings.</li>"}</ul>
  <h2>Machine-readable report</h2>
  <pre>{html.escape(dumps_json(report, pretty=True))}</pre>
</main>
</body>
</html>
"""


def render_build_html(report: BuildReport) -> str:
    warning_items = "".join(f"<li>{html.escape(warning)}</li>" for warning in report.warnings[:50])
    error_items = "".join(f"<li>{html.escape(error)}</li>" for error in report.errors[:50])
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Contexte Build Report</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:2rem;}} main{{max-width:900px;margin:auto;}} .card{{border:1px solid #ddd;border-radius:12px;padding:1rem;margin:.75rem 0;}}</style></head>
<body><main><h1>Contexte Build Report</h1>
<div class=\"card\"><strong>Source:</strong> {html.escape(report.source_root)}</div>
<div class=\"card\"><strong>Documents:</strong> {report.document_count}<br><strong>Chunks:</strong> {report.chunk_count}<br><strong>Security findings:</strong> {report.security_finding_count}</div>
<h2>Warnings</h2><ul>{warning_items or "<li>No warnings.</li>"}</ul>
<h2>Errors</h2><ul>{error_items or "<li>No errors.</li>"}</ul>
<pre>{html.escape(dumps_json(report, pretty=True))}</pre>
</main></body></html>"""


def write_build_report(report: BuildReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".json":
        write_json(output, report, pretty=True)
    else:
        output.write_text(render_build_html(report), encoding="utf-8")


def _metric(label: str, value: object) -> str:
    return f'<div class="card"><div class="label">{html.escape(label)}</div><div class="value">{html.escape(str(value))}</div></div>'
