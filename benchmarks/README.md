# Benchmarks

This directory holds the public benchmark suite for Contexte. It is used
both as a regression harness in CI (`python scripts/run_benchmarks.py`)
and as the canonical place to grow the project's evaluation surface.

## Layout

- `corpora/` — public input corpora used as benchmark fixtures.
- `expected/` — golden manifests produced by the runner (one file per
  corpus under `expected/manifests/`). Used to detect regressions in
  pack structure, document/chunk IDs, and chunking behavior.
- `metrics/` — benchmark definitions, score descriptions, and result
  snapshots (reserved for future work).
- `tmp/` — packs produced during a benchmark run. Safe to delete.

## Running

```bash
python scripts/run_benchmarks.py            # run all corpora and diff
python scripts/run_benchmarks.py -v         # show per-corpus error detail
python scripts/run_benchmarks.py --update   # refresh golden manifests
```

The runner:

1. Builds each corpus with `ctx build` (using a deterministic timestamp).
2. Calls `ctx inspect --json` and compares the result to the matching
   `expected/manifests/<corpus>.json` golden snapshot.
3. Walks every chunk in the pack and verifies that its text is faithful
   to the underlying document blocks (no fabricated content).

### Portability across machines

To keep golden snapshots stable across machines (local dev vs. CI
runners), the runner normalizes host-dependent fields before diffing:

- `path` → `<TMP>/<corpus>.ctxpack`
- `manifest.source_summary.source_root` → `<CORPORA>/<corpus>`
- `manifest.checksums[*]` values → `<dynamic>` (keys are preserved, so
  the set of artifacts and the stable, content-addressed document IDs
  are still asserted).

`created_at`, `modified_at`, and `pack_id` are also ignored during the
diff (`pack_id` is deterministic but already covered by the doc/chunk
ID checksums embedded in the manifest checksum keys).

## Current corpora

- `simple_docs` — minimal markdown smoke test.
- `tables` / `docx_tables` — table-handling regression cases.
- `pdf_text` — PDF text extraction.
- `security_findings` — secret / PII detection paths.
- `duplicates` — duplicate-document handling.
- `stale_conflicts` — stale/conflict detection scenarios.
- `bad_inputs` — error-path coverage for malformed inputs.

## Planned future work

- Retrieval-oriented benchmark fixtures and scoring.
- Public evaluation reports under `metrics/`.
- Larger / domain-specific corpora.
