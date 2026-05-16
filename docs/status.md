# Contexte: Specification vs. Implementation Status

This document tracks the delta between the [Complete Project Specification](rfc/0000-project-spec.md) and the current implementation.

## Core Architecture

| Feature | Spec | Implemented | Tested | Stability |
| :--- | :--- | :--- | :--- | :--- |
| **Local-first** | Mandatory | Yes | Verified | Stable |
| **No Network in Core** | Mandatory | Yes | Verified | Stable |
| **Deterministic Packs** | Mandatory | Yes | Yes | Stable |
| **Post-build Validation** | Mandatory | Yes | Yes | Stable |
| **Hardened Reader** | Mandatory | Yes | Yes | Stable |
| **Deep IR Validation** | Mandatory | Yes | Yes | Stable |

## CLI Commands (`ctx`)

| Command | Spec | Implemented | JSON Output | Quiet/Verbose |
| :--- | :--- | :--- | :--- | :--- |
| **`probe`** | Mandatory | Yes | Yes | Yes |
| **`build`** | Mandatory | Yes | Yes | Yes |
| **`inspect`** | Mandatory | Yes | Yes | Yes |
| **`eval`** | Mandatory | Yes | Yes | Yes |
| **`export`** | Mandatory | Yes | Yes | Yes |
| **`report`** | Mandatory | Yes | Yes | Yes |
| **`validate`** | Optional | Yes | Yes | Yes |
| **`diff`** | Optional | Yes | Yes | Yes |
| **`schemas`** | Optional | Yes | Yes | Yes |
| **`sign`** | Optional | Yes | No | Yes (CLI tests) |
| **`verify`** | Optional | Yes | No | Yes (CLI tests) |
| **`serve`** | Optional | Placeholder | - | - |
| **`plugins`** | Optional | Yes | Yes | Yes |

`ctx sign` and `ctx verify` deal with cryptographic authenticity of the
manifest (Ed25519). `ctx validate` is independent: it checks structural
integrity and member checksums. The two are complementary, not redundant.

## Context IR (Intermediate Representation)

| Component | Spec | Implemented | Deep Validation |
| :--- | :--- | :--- | :--- |
| **`ContextDocument`** | Yes | Yes | Full |
| **`Block`** | Yes | Yes | Full |
| **`ContextChunk`** | Yes | Yes | Full |
| **`SourceRef`** | Yes | Yes | Yes |
| **`SecuritySummary`** | Yes | Yes | Yes |
| **`Lineage`** | Yes | Yes | Yes |

## Ingestion & Decoders

| Format | Text | Tables | Headings | Spans | Stability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`.md`** | Yes | Partial | Yes | Yes | Stable |
| **`.txt`** | Yes | No | No | Yes | Stable |
| **`.html`** | Yes | Partial | Yes | Partial | Stable |
| **`.pdf`** | Yes | Weak | Weak | No | Alpha |
| **`.docx`** | Yes | Yes | Yes | No | Alpha |
| **`.csv`** | Yes | Yes | N/A | Yes | Stable |
| **`.json`** | Yes | N/A | N/A | No | Stable |

## Security & Safety

| Feature | Spec | Implemented | Policy Control |
| :--- | :--- | :--- | :--- |
| **PII Detection** | Regex | Yes | Basic |
| **Secret Detection** | Regex | Yes | Basic |
| **Prompt Injection** | Heuristic | Yes | Basic |
| **Redaction** | Mandatory | Yes | Yes (Export) |
| **ACL Metadata** | Roadmap | No | No |
| **Pack Signing** | Roadmap | Yes (Ed25519, alpha) | Manual via `ctx sign` / `--sign` |

## Roadmap Items Status

- [x] **v0.1**: Local context compiler, `.ctxpack`, Context IR, Decoders, Chunking, Eval, Security scans, JSONL/Markdown export, Ed25519 manifest signing (alpha), portable benchmark suite.
- [ ] **v0.2 (interop)**: LlamaIndex/LangChain exporters hardening, Stabilized plugin API, Local HTTP read-only adapter, Decoder integration polish.
- [ ] **v0.3**: Experimental MCP read-only adapter, MCP security scanner, Tool-description sanitizer.
- [ ] **v0.4**: Stronger PII detection, ACL metadata, Policy engine, OCR / Docling / Unstructured plugins.
- [ ] **v1.0**: Stable IR, stable `.ctxpack`, migration tools, production docs.

LlamaIndex and LangChain exporters already exist as preview implementations
(`ctx export --to llamaindex|langchain`) but their schema and metadata
contracts are not yet stable; that is the v0.2 deliverable.
