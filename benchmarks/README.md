# Benchmarks

This directory is the public benchmark scaffold for Contexte.

It exists before the benchmark suite is fully implemented so the repository makes its evaluation ambition explicit.

## Layout

- `corpora/` — public input corpora, fixture manifests, or references to downloadable datasets.
- `expected/` — expected packs, exports, summaries, or golden outputs.
- `metrics/` — benchmark definitions, score descriptions, and result snapshots.

## Current status

This scaffold is intentionally lightweight in v0.1 alpha.

Planned future work includes:

- public corpora for parsing and chunking regression checks;
- retrieval-oriented benchmark fixtures;
- citation faithfulness checks;
- stale/conflict detection scenarios;
- reproducible expected outputs and score reports.
