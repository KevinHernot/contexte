# Architecture

Contexte is organized as a local-first pipeline:

```text
source discovery -> decoding -> normalization -> security scanning -> chunking -> evaluation -> pack writing -> export/report
```

## Packages

- `contexte.core`: config, hashing, IDs, discovery, build pipeline.
- `contexte.ir`: Pydantic models, serialization, validation, schema helpers.
- `contexte.decoders`: file decoders for v0.1 formats.
- `contexte.chunkers`: fixed and heading-aware chunkers.
- `contexte.security`: PII, secret, and prompt-injection scanners.
- `contexte.pack`: `.ctxpack` writer/reader/manifest/layout.
- `contexte.eval`: basic eval suite and HTML report rendering.
- `contexte.exporters`: JSONL and Markdown exporters.
- `contexte.cli`: Typer/Rich command-line interface.
- `contexte.plugins`: optional plugin registry and entry-point loader.
- `contexte.mcp`: optional read-only adapter placeholders and local lexical search helpers. MCP compatibility is planned, but not part of the v0.1 trust core.

## Determinism

The writer uses stable internal paths, stable IDs, sorted ZIP members, fixed ZIP timestamps, and checksums. Build timestamps still reflect when a pack was created.
