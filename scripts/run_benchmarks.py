#!/usr/bin/env python3
"""Contexte Benchmark Runner & Golden Test Suite.

The runner builds each corpus in ``benchmarks/corpora`` with the local
``contexte`` CLI, then compares the resulting pack to a golden
``benchmarks/expected/manifests/<corpus>.json`` snapshot.

To stay portable across machines (including GitHub Actions runners), the
comparison normalizes any data that is inherently absolute-path or
host-dependent before diffing:

* ``path`` -> ``<TMP>/<corpus>.ctxpack``
* ``manifest.source_summary.source_root`` -> ``<CORPORA>/<corpus>``
* ``manifest.checksums``: keys are preserved (so we still assert the same
  set of artifacts is produced and that document IDs are deterministic),
  but values are replaced with ``"<dynamic>"`` because the underlying
  files embed absolute ``file://`` URIs (in JSONL payloads and the
  ``normalized/markdown`` front-matter), as well as build-report fields.

Doc/chunk/pack IDs themselves are content-addressed from *relative*
paths and are therefore stable across machines; they remain part of the
golden snapshot.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Contexte Benchmark CLI")

ROOT = Path(__file__).parent.parent
CORPORA_DIR = ROOT / "benchmarks" / "corpora"
EXPECTED_DIR = ROOT / "benchmarks" / "expected"
TEMP_DIR = ROOT / "benchmarks" / "tmp"

# Placeholder used in place of host-dependent checksum values.
DYNAMIC_CHECKSUM_PLACEHOLDER = "<dynamic>"


def run_ctx(args: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["FORCE_COLOR"] = "0"
    env["CONTEXTE_DETERMINISTIC_TIMESTAMP"] = "2026-01-01T00:00:00Z"
    return subprocess.run(
        [sys.executable, "-m", "contexte.cli.app", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def normalize_inspect_payload(data: dict[str, Any], corpus_name: str) -> dict[str, Any]:
    """Replace machine-specific fields with stable placeholders.

    Mutates and returns ``data`` for convenience.
    """
    data["path"] = f"<TMP>/{corpus_name}.ctxpack"

    manifest = data.get("manifest") or {}
    summary = manifest.get("source_summary") or {}
    if "source_root" in summary:
        summary["source_root"] = f"<CORPORA>/{corpus_name}"

    # All checksum values are host-dependent (JSONL/markdown payloads
    # embed absolute ``file://`` URIs, and reports include timing info).
    # Keep the keys so we still assert the set of artifacts and stable
    # doc IDs, but normalize the values.
    checksums = manifest.get("checksums") or {}
    for key in checksums:
        checksums[key] = DYNAMIC_CHECKSUM_PLACEHOLDER

    return data


def compare_json(
    actual: Any,
    expected: Any,
    path: str = "",
    ignore_keys: list[str] | None = None,
) -> list[str]:
    ignore_keys = ignore_keys or ["created_at", "pack_id", "modified_at"]
    errors: list[str] = []
    if type(actual) is not type(expected):
        errors.append(f"{path}: type mismatch ({type(actual)} vs {type(expected)})")
        return errors

    if isinstance(actual, dict):
        for k in actual:
            if k in ignore_keys:
                continue
            if k not in expected:
                errors.append(f"{path}: unexpected key '{k}'")
            else:
                errors.extend(
                    compare_json(actual[k], expected[k], f"{path}.{k}" if path else k, ignore_keys)
                )
        for k in expected:
            if k in ignore_keys:
                continue
            if k not in actual:
                errors.append(f"{path}: missing key '{k}'")
    elif isinstance(actual, list):
        if len(actual) != len(expected):
            errors.append(f"{path}: list length mismatch ({len(actual)} vs {len(expected)})")
        else:
            for i, (a, e) in enumerate(zip(actual, expected, strict=True)):
                errors.extend(compare_json(a, e, f"{path}[{i}]", ignore_keys))
    elif actual != expected:
        # Handle float epsilon if needed, but for now exact match for stability
        errors.append(f"{path}: value mismatch ('{actual}' vs '{expected}')")

    return errors


def check_faithfulness(pack_path: Path) -> list[str]:
    from contexte.pack.reader import PackReader

    errors = []
    reader = PackReader(pack_path)
    docs = {d.id: d for d in reader.iter_documents()}

    for chunk in reader.iter_chunks():
        source_text = ""
        for ref in chunk.source_refs:
            doc = docs.get(ref.document_id)
            if not doc:
                errors.append(f"Chunk {chunk.id}: document {ref.document_id} missing")
                continue
            for b_id in ref.block_ids:
                block = next((b for b in doc.blocks if b.id == b_id), None)
                if not block:
                    errors.append(f"Chunk {chunk.id}: block {b_id} missing")
                else:
                    source_text += getattr(block, "text", "") or getattr(block, "markdown", "")

        # Simple normalization for comparison
        c_norm = "".join(chunk.text.split())
        s_norm = "".join(source_text.split())
        if c_norm not in s_norm:
            errors.append(f"Chunk {chunk.id}: faithfulness violation (text not in source)")
    return errors


@app.command()
def run(
    update: bool = typer.Option(False, "--update", "-u", help="Update expected (golden) outputs."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed errors."),
):
    """Run all benchmarks."""
    TEMP_DIR.mkdir(exist_ok=True)

    results = []
    failed = False

    corpora = sorted([d for d in CORPORA_DIR.iterdir() if d.is_dir()])

    for corpus in corpora:
        name = corpus.name
        pack_path = TEMP_DIR / f"{name}.ctxpack"

        # 1. Build
        build_res = run_ctx(["build", str(corpus), "--to", str(pack_path), "--force"])
        if build_res.returncode != 0:
            results.append({"name": name, "status": "FAIL", "reason": "Build failed"})
            failed = True
            continue

        # 2. Extract Data for Comparison
        inspect_res = run_ctx(["inspect", str(pack_path), "--json"])
        if inspect_res.returncode != 0:
            results.append({"name": name, "status": "FAIL", "reason": "Inspect failed"})
            failed = True
            if verbose:
                console.print(f"  [red]{name} inspect stderr:[/red] {inspect_res.stderr}")
            continue
        actual_data = json.loads(inspect_res.stdout)

        # Normalize machine-specific fields so golden comparisons are
        # portable across machines (e.g. local vs. GitHub Actions runners).
        normalize_inspect_payload(actual_data, name)

        expected_file = EXPECTED_DIR / "manifests" / f"{name}.json"

        if update:
            expected_file.parent.mkdir(parents=True, exist_ok=True)
            with open(expected_file, "w") as f:
                json.dump(actual_data, f, indent=2)
            results.append({"name": name, "status": "UPDATED", "reason": "Golden updated"})
            continue

        if not expected_file.exists():
            results.append({"name": name, "status": "SKIP", "reason": "No expected data"})
            continue

        with open(expected_file) as f:
            expected_data = json.load(f)

        errors = compare_json(actual_data, expected_data)

        # 3. Faithfulness
        faith_errors = check_faithfulness(pack_path)
        errors.extend(faith_errors)

        if errors:
            results.append({"name": name, "status": "FAIL", "reason": f"{len(errors)} issues"})
            failed = True
            if verbose:
                for err in errors:
                    console.print(f"  [red]Error in {name}: {err}[/red]")
        else:
            results.append({"name": name, "status": "PASS", "reason": "Stable & Faithful"})

    # 4. Summary Table
    table = Table(title="Contexte Benchmark Results")
    table.add_column("Corpus", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")

    for res in results:
        status_style = (
            "green"
            if res["status"] in ["PASS", "UPDATED"]
            else "yellow"
            if res["status"] == "SKIP"
            else "red"
        )
        table.add_row(
            res["name"], f"[{status_style}]{res['status']}[/{status_style}]", res["reason"]
        )

    console.print(table)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    app()
