"""Portability test for the benchmark runner.

Re-runs ``scripts/run_benchmarks.py`` from a temporary directory whose
absolute path is unrelated to the developer's checkout, so that any
golden snapshot that accidentally captures host-specific paths fails
locally instead of only on CI.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_benchmarks_pass_from_alternate_path(tmp_path: Path) -> None:
    workdir = tmp_path / "contexte-portable"
    (workdir / "scripts").mkdir(parents=True)
    (workdir / "benchmarks").mkdir()

    shutil.copy2(ROOT / "scripts" / "run_benchmarks.py", workdir / "scripts" / "run_benchmarks.py")
    shutil.copytree(ROOT / "benchmarks" / "corpora", workdir / "benchmarks" / "corpora")
    shutil.copytree(ROOT / "benchmarks" / "expected", workdir / "benchmarks" / "expected")

    result = subprocess.run(
        [sys.executable, "scripts/run_benchmarks.py"],
        cwd=workdir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Benchmark runner failed from alternate path. "
        "Golden snapshots likely contain host-specific data.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
