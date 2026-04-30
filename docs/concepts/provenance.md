# Provenance

Provenance is mandatory in Contexte.

Each chunk includes `source_refs` with:

- `document_id`;
- block IDs;
- source URI;
- optional page range;
- optional line range.

This lets downstream RAG systems cite source files, pages, lines, and sections rather than returning unsupported text.

## Lineage

Every document records decoder ID, decoder version when available, pipeline version, config hash, and creator.
