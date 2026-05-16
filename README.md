# Contexte

Contexte is an open-source toolkit for compiling raw documents, repositories, and data sources into trustworthy AI context.

It provides:

- a CLI named `ctx`;
- a portable `.ctxpack` archive format;
- a versioned Context IR;
- document ingestion and normalization;
- chunking with provenance;
- security checks for PII, secrets, and prompt-injection-like text;
- RAG readiness evaluation reports;
- exports to JSONL and normalized Markdown.

> Status: v0.1 alpha. The core is local-first, offline-friendly, and intentionally lightweight. See [Implementation Status](docs/status.md) for details on spec parity.

## Why?

AI systems do not only need better models. They need better context.

Contexte helps transform messy raw data into context that is portable, auditable, citable, and ready for retrieval or agent workflows.

## Install

```bash
pip install contexte
```

For local development from this repository:

```bash
pip install -e ".[dev]"
```

## Quickstart

```bash
ctx build ./docs --to docs.ctxpack --report
ctx validate docs.ctxpack
ctx inspect docs.ctxpack
ctx eval docs.ctxpack --report eval.html
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
```

Example output from `ctx inspect`:

```text
Contexte Pack

Path: docs.ctxpack
Schema: 0.1.0
Documents: 6
Chunks: 24
Security findings: 2
Build warnings: 1
```

Example output from `ctx eval`:

```text
RAG readiness score: 86/100
This is a heuristic quality signal, not a guarantee of RAG performance.
Documents: 6
Chunks: 24
Average chunk length: 1,240 chars
Chunks without citations: 0
PII findings: 1
Secret findings: 1
Prompt injection warnings: 0
```

## Core concepts

- **Source**: an input object, currently a local file or directory.
- **Decoder**: converts a source file into Context IR documents.
- **Context IR**: the canonical JSON-serializable document/block/chunk representation.
- **Chunk**: a retrieval-ready unit with stable ID, provenance, security metadata, and quality metadata.
- **Context Pack**: a `.ctxpack` ZIP archive containing documents, chunks, sources, checksums, reports, and metadata.
- **Eval report**: a machine-readable and human-readable quality/safety report.

## Core guarantees

Contexte is designed around a set of "hard" guarantees that distinguish it from standard ingestion scripts:

1.  **Local-first & No Network**: The core library and CLI will never perform network calls or upload data.
2.  **Deterministic Layout**: Given the same inputs and config, a `.ctxpack` will have a deterministic internal structure and member order.
3.  **Integrity & Trust**: Every pack includes mandatory checksums and a verifiable manifest.
4.  **Provenance**: Every chunk is linked to its source document, block IDs, and original URI.
5.  **Auditability**: Security findings and extraction errors are preserved as first-class metadata, never suppressed.

## CLI commands

```bash
ctx probe ./docs
ctx build ./docs --to docs.ctxpack --report --force
ctx build ./docs --to docs.ctxpack --sign ./keys/contexte_private.pem
ctx validate docs.ctxpack
ctx inspect docs.ctxpack --json
ctx eval docs.ctxpack --report eval.html
ctx report docs.ctxpack --output report.html
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
ctx export docs.ctxpack --to jsonl --output chunks.jsonl --redact
ctx export docs.ctxpack --to markdown --output normalized/
ctx export docs.ctxpack --to langchain --output chunks.langchain.json
ctx export docs.ctxpack --to llamaindex --output chunks.llamaindex.json
ctx sign docs.ctxpack --key ./keys/contexte_private.pem
ctx verify docs.ctxpack --key ./keys/contexte_public.pem
ctx plugins list
```

`ctx validate` checks structural integrity (manifest, member files,
checksums, IR models). `ctx verify` adds cryptographic authenticity of
`manifest.json` against an Ed25519 public key — the two are
complementary, not redundant. `ctx build --sign` is a convenience that
runs the build and then signs the resulting pack in place.

The optional `--redact` flag replaces detected PII and secrets with
`[REDACTED:label]` placeholders in the export only; the canonical `.ctxpack`
artifact is never mutated.

`ctx serve` exists as an explicit placeholder for future read-only serving adapters. It is not part of the v0.1 core promise. v0.1 includes only local lexical helper functions under `contexte.mcp.tools`.

Planned future adapter shape:

```bash
ctx serve handbook.ctxpack --http --read-only
ctx serve handbook.ctxpack --mcp --read-only
```

## Supported v0.1 inputs

- Markdown (`.md`)
- Text (`.txt`)
- HTML (`.html`, `.htm`)
- PDF (`.pdf`, text extraction only; no OCR)
- DOCX (`.docx`)
- CSV (`.csv`)
- JSON (`.json`)

Bad PDFs, malformed DOCX files, empty documents, and unsupported files produce warnings instead of silent corruption.

## Local-first security posture

Core Contexte does not upload data, call model providers, or require embeddings. Security scanners mark:

- email/phone/IP/card/SSN/IBAN-like PII;
- AWS/GitHub/Slack/API/private-key-like secrets;
- prompt-injection-like phrases such as “ignore previous instructions”.

Findings are metadata. The canonical `.ctxpack` is never modified by the
scanners. Use `ctx export --redact` for an opt-in redaction pass that produces
placeholder-substituted JSONL or Markdown derivatives suitable for sharing.

ACL metadata and policy enforcement are roadmap items, not a v0.1 guarantee.

## Public benchmark scaffold

The repository includes a public benchmark scaffold under `benchmarks/` for future shared corpora, expected outputs, and metrics.

## Development

```bash
ruff check .
ruff format --check .
mypy src
pytest --cov=contexte
```

CI runs the same quality gates.

## Roadmap

- **v0.1**: local context compiler, `.ctxpack`, Context IR, decoders, chunking, eval, security scans, JSONL/Markdown export.
- **v0.2**: local HTTP read-only adapter, LlamaIndex/LangChain exporters, stabilized plugin API, better decoder integrations.
- **v0.3**: experimental MCP read-only adapter, MCP security scanner, manifest signing, tool-description sanitization.
- **v0.4**: stronger PII detection, ACL metadata, policy engine, Docling/Unstructured/OCR integrations, pack signing.
- **v1.0**: stable Context IR, stable `.ctxpack`, migration tools, production docs.

## Contributing

See `CONTRIBUTING.md`. Significant schema, pack, plugin, security, or CLI changes should go through RFCs in `docs/rfc/`.

## License

Apache-2.0. See `LICENSE`.
