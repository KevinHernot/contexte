# RFC 0001: Context IR

## Status

Accepted for v0.1 alpha.

## Summary

Context IR is the canonical JSON-serializable representation for documents, blocks, chunks, provenance, security metadata, quality metadata, and extraction errors.

## Motivation

AI context needs traceability and validation before it is used by retrieval, agents, MCP tools, or fine-tuning workflows.

## Decision

Use Pydantic models in `src/contexte/ir/models.py` and independent schema version `0.1.0`.
