# Chunking

Contexte v0.1 includes two production chunkers and one explicit placeholder.

## Heading-aware chunker

Default strategy. It tracks heading hierarchy, groups paragraphs under headings, and attaches section paths to chunks.

```bash
ctx build ./docs --to docs.ctxpack --chunker heading
```

## Fixed chunker

Groups blocks until `max_chars`, then starts a new chunk. Large text is split with optional overlap while preserving citations.

```bash
ctx build ./docs --to docs.ctxpack --chunker fixed --max-chars 2000
```

## Semantic placeholder

`semantic` is reserved for plugin-backed embedding or model-assisted chunking.

```text
Semantic chunking requires plugin: contexte-semantic
```

## Guarantees

- Empty chunks are skipped.
- Source block IDs are preserved.
- Code/table blocks are kept together where possible.
- Chunks include source references for citation coverage.
