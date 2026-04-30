# `.ctxpack`

A `.ctxpack` is a deterministic ZIP archive for portable AI context.

Required layout:

```text
manifest.json
documents/documents.jsonl
chunks/chunks.jsonl
reports/build-report.json
security/findings.jsonl
metadata/sources.jsonl
metadata/pipeline.json
metadata/checksums.json
```

Optional layout:

```text
normalized/markdown/<document_id>.md
eval/basic-report.json
eval/basic-report.html
embeddings/
indexes/
original/
```

## Manifest

`manifest.json` declares schema version, pack ID, creator, source summary, feature flags, and checksums.

## Checksums

The writer records SHA-256 checksums for archive members. The reader validates them by default.

## Atomic writes

The writer builds a temporary directory, zips to a partial file, and replaces the target only after a successful archive write.
