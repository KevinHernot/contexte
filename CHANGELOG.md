# Changelog

All notable changes to Contexte will be documented in this file.

## Unreleased

- Added `contexte.security.redaction` with `redact_text` / `redact_chunk_text`
  helpers that mask PII and secret findings with `[REDACTED:label]`
  placeholders. Prompt-injection findings are intentionally excluded by default.
- Added `--redact` flag to `ctx export` for both JSONL and Markdown formats.
  Redaction operates on derived exports only; the canonical `.ctxpack` is never
  mutated.
- Added Ed25519 manifest signing via `contexte.core.signing`, exposed through
  `ctx sign`, `ctx verify`, and `ctx build --sign`. Signatures cover
  `manifest.json` (which itself pins every other pack member by checksum), so
  any post-build tampering is detected. `ctx validate` continues to cover
  structural integrity; `ctx verify` adds cryptographic authenticity.
- Added LlamaIndex and LangChain exporters under `contexte.exporters`,
  reachable via `ctx export --to llamaindex` and `--to langchain`.
- Added a portable benchmark runner (`scripts/run_benchmarks.py`) with golden
  manifest snapshots under `benchmarks/expected/manifests/` and a
  cross-machine portability test
  (`tests/integration/test_benchmark_portability.py`). Wired into CI so
  regressions in pack structure, document IDs, or chunk faithfulness fail
  the build.
- Promoted `CONTEXTE_PROJECT_SPEC.md` into `docs/rfc/0000-project-spec.md`
  alongside the existing IR / pack / plugin RFCs to keep the scope document
  versioned with other normative specifications.
- Added unit tests for IR validation (`validate_document`, `validate_chunk`,
  `validate_manifest`), JSON schema export, the v0.1 security policy, the
  redaction module, and signing/verification.

## 0.1.0 - 2026-04-29

- Initial local-first context compiler implementation.
- Added `ctx` CLI with `probe`, `build`, `inspect`, `validate`, `eval`, `export`, and `report` commands.
- Added Context IR models, `.ctxpack` writer/reader, decoders, chunkers, security scanners, eval metrics, reports, fixtures, and tests.
