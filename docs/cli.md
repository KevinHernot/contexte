# CLI reference

All commands support `--help`. Commands that print structured data support `--json`.

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
```

Options:

- `--to`: output `.ctxpack` path;
- `--chunker`: `heading`, `fixed`, or `semantic`;
- `--max-chars`: maximum chunk size;
- `--include` / `--exclude`: repeated glob filters;
- `--report`: write adjacent HTML build report;
- `--force`: overwrite output.

`semantic` is a v0.1 placeholder and reports that `contexte-semantic` is required.

## `ctx validate`

Validate manifest, required files, JSONL, checksums, and models.

```bash
ctx validate docs.ctxpack
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
ctx export docs.ctxpack --to markdown --output normalized/
```

## `ctx report`

Generate a human-readable eval report.

```bash
ctx report docs.ctxpack --output report.html
```

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
