# RFC 0002: `.ctxpack`

## Status

Accepted for v0.1 alpha.

## Summary

A `.ctxpack` is a deterministic ZIP archive containing manifest, documents, chunks, reports, security findings, source metadata, pipeline config, and checksums.

## Decision

Use JSON/JSONL files inside a ZIP archive. Validate checksums by default.
