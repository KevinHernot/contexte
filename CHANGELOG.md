# Changelog

All notable changes to Contexte will be documented in this file.

## Unreleased

- Added `contexte.security.redaction` with `redact_text` / `redact_chunk_text`
  helpers that mask PII and secret findings with `[REDACTED:label]`
  placeholders. Prompt-injection findings are intentionally excluded by default.
- Added `--redact` flag to `ctx export` for both JSONL and Markdown formats.
  Redaction operates on derived exports only; the canonical `.ctxpack` is never
  mutated.
- Promoted `CONTEXTE_PROJECT_SPEC.md` into `docs/rfc/0000-project-spec.md`
  alongside the existing IR / pack / plugin RFCs to keep the scope document
  versioned with other normative specifications.
- Added unit tests for IR validation (`validate_document`, `validate_chunk`,
  `validate_manifest`), JSON schema export, the v0.1 security policy, and the
  new redaction module. Coverage rose from ~79% to ~81%.

## 0.1.0 - 2026-04-29

- Initial local-first context compiler implementation.
- Added `ctx` CLI with `probe`, `build`, `inspect`, `validate`, `eval`, `export`, and `report` commands.
- Added Context IR models, `.ctxpack` writer/reader, decoders, chunkers, security scanners, eval metrics, reports, fixtures, and tests.
