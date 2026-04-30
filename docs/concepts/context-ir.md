# Context IR

Context IR is Contexte's canonical intermediate representation. It is JSON-serializable, versioned, and designed to preserve provenance.

## Document

A document contains:

- stable `id`;
- `schema_version`;
- `source` metadata;
- extracted blocks;
- security summary;
- lineage;
- structured extraction errors.

## Block

A block is the smallest structured unit extracted from a document. Supported block types include headings, paragraphs, list items, tables, code, quotes, metadata, page breaks, and unknown blocks.

Blocks may include source spans, page numbers, bounding boxes, hierarchy metadata, and confidence values.

## Chunk

A chunk is retrieval-ready text derived from blocks. Chunks include:

- stable `id`;
- `document_id`;
- text;
- title and section path;
- `source_refs` with block IDs and source URI;
- token/character estimates;
- security and quality metadata.

## Stable IDs

- Documents: `doc_<16-char-hash>`
- Blocks: `blk_<document-short-id>_<index>`
- Chunks: `chk_<document-short-id>_<strategy>_<index>`
