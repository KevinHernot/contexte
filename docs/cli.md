# CLI reference

Common options:
- `--help`: Show usage information.
- `--json`: Print machine-readable JSON output.
- `--quiet`: Suppress human-oriented progress and summary output.
- `--verbose`: Show additional details and explanations.

## `ctx probe`

Inspect files before building.

```bash
ctx probe ./docs
ctx probe ./docs --json
```

## `ctx build`

Build a portable context pack.

```bash
ctx build ./docs --to docs.ctxpack --chunker heading --max-chars 3000 --report --force
ctx build ./docs --to docs.ctxpack --sign ./keys/contexte_private.pem
```

Options:

- `--to`: output `.ctxpack` path;
- `--chunker`: `heading`, `fixed`, or `semantic`;
- `--max-chars`: maximum chunk size;
- `--include` / `--exclude`: repeated glob filters;
- `--report`: write adjacent HTML build report;
- `--force`: overwrite output;
- `--sign`: Ed25519 private key used to sign `manifest.json` in-place
  (equivalent to running `ctx sign` after the build).

`semantic` is a v0.1 placeholder and reports that `contexte-semantic` is required.

## `ctx validate`

Validate **structural integrity**: manifest, required files, JSONL, member
checksums, and IR models. Does **not** check cryptographic authenticity —
use `ctx verify` for that.

```bash
ctx validate docs.ctxpack
ctx validate docs.ctxpack --strict --skip-checksums
```

## `ctx inspect`

Print pack summary.

```bash
ctx inspect docs.ctxpack
ctx inspect docs.ctxpack --json
```

## `ctx eval`

Run the basic eval suite.

```bash
ctx eval docs.ctxpack --suite basic --report eval.html
```

## `ctx export`

Export chunks or normalized documents.

```bash
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
ctx export docs.ctxpack --to jsonl --output chunks.jsonl --redact
ctx export docs.ctxpack --to markdown --output normalized/
ctx export docs.ctxpack --to langchain --output chunks.langchain.json
ctx export docs.ctxpack --to llamaindex --output chunks.llamaindex.json
```

`langchain` and `llamaindex` are preview exporters: they produce JSON
suitable for direct loading into their respective document/node loaders.
Schema stabilisation is a v0.2 deliverable.

The optional `--redact` flag replaces detected PII and secrets with `[REDACTED:label]` placeholders in the export only. The canonical `.ctxpack` archive is never modified.

## `ctx report`

Generate a human-readable eval report.

```bash
ctx report docs.ctxpack --output report.html
```

## `ctx sign`

Sign a context pack's `manifest.json` with an Ed25519 private key. The
signature is stored inside the pack at `metadata/signature.json`. Because
the manifest pins every other pack member by checksum, signing it
authenticates the entire pack.

```bash
# Sign with an existing key
ctx sign docs.ctxpack --key ./keys/contexte_private.pem

# Generate a fresh keypair into ./keys/ and sign with the new private key
ctx sign docs.ctxpack --gen-key --output-dir ./keys
```

Options:

- `--key`: path to an Ed25519 private key (PEM, PKCS#8);
- `--gen-key`: generate a new keypair in `--output-dir` and use it;
- `--output-dir`: directory for generated keys (default: `.`).

The pack is rewritten in place; only `metadata/signature.json` is added.

## `ctx verify`

Verify a context pack's signature against a known public key.

```bash
ctx verify docs.ctxpack --key ./keys/contexte_public.pem
```

`ctx verify` performs both structural validation (same checks as
`ctx validate`) and cryptographic verification of `manifest.json` against
the supplied Ed25519 public key. Failure modes that are reported:

- pack is not signed;
- signature does not match the manifest under this public key;
- pack contents have been tampered with after signing (the manifest's
  member checksums no longer match).

## `ctx plugins list`

List discovered optional plugins.

```bash
ctx plugins list
```

## `ctx serve`

`ctx serve` is a placeholder in v0.1. Serving is not part of the trusted core and future adapters are expected to be read-only.

Planned future shape:

```bash
ctx serve docs.ctxpack --http --read-only --port 8787
ctx serve docs.ctxpack --mcp --read-only --port 8787
```

Current recommendation: use `ctx export` for portable outputs and `contexte.mcp.tools` for local lexical helpers.
