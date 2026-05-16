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
| **`serve`** | Optional | Placeholder | - | - |
| **`plugins`** | Optional | Yes | Yes | Yes |

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
| **Pack Signing** | Roadmap | No | No |

## Roadmap Items Status

- [x] **v0.1**: Local context compiler, `.ctxpack`, Context IR, Decoders, Chunking, Eval, Security scans, JSONL/Markdown export.
- [ ] **v0.2**: Local HTTP read-only adapter, LlamaIndex/LangChain exporters, Stabilized plugin API.
- [ ] **v0.3**: Experimental MCP read-only adapter, MCP security scanner, Manifest signing.
- [ ] **v0.4**: Stronger PII detection, ACL metadata, Policy engine.
- [ ] **v1.0**: Stable IR, stable `.ctxpack`, migration tools, production docs.
