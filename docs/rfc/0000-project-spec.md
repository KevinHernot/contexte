# Contexte — Complete Project Specification

> **Purpose of this file**  
> This Markdown file is designed to be used as a complete implementation brief for an advanced coding agent such as GPT-5.5 running in Codex.  
> The goal is that an AI coding agent can read this file and implement the project with minimal ambiguity.

---

## 0. Project Summary

**Project name:** Contexte  
**CLI name:** `ctx`  
**Portable package format:** `.ctxpack`  
**Core specification:** Context IR  
**License target:** Apache-2.0  
**Project type:** Open source infrastructure  
**Primary goal:** Compile messy raw data into trustworthy, portable AI context.

### One-sentence definition

**Contexte is an open-source toolkit for compiling raw documents, repositories, and data sources into trustworthy AI context with provenance, citations, chunking, evaluation, security checks, and interoperable exports.**

### Analogy

Contexte should be to AI context what **FFmpeg** is to media:

```text
FFmpeg:
raw media -> decode -> filter -> encode -> output

Contexte:
raw sources -> decode -> normalize -> secure -> chunk -> evaluate -> package -> serve/export
```

### Core promise

```bash
ctx build ./docs --to handbook.ctxpack --report
ctx inspect handbook.ctxpack
ctx eval handbook.ctxpack
ctx export handbook.ctxpack --to jsonl
```

Future optional read-only adapters (not part of the v0.1 core promise):

```bash
ctx serve handbook.ctxpack --http --read-only
ctx serve handbook.ctxpack --mcp --read-only
```

---

## 1. Mission, Principles, and Non-Goals

### 1.1 Mission

Create a neutral, local-first, open-source infrastructure layer that turns heterogeneous data into reliable AI-ready context.

Contexte should help developers, AI engineers, researchers, public institutions, and companies answer:

- What data do I have?
- Can it be parsed?
- Is it safe to use?
- Is it fresh?
- Is it duplicated?
- Is it correctly chunked?
- Can it be cited?
- Can it be evaluated?
- Can it be used by RAG, agents, vector stores, fine-tuning workflows, and future read-only HTTP/MCP adapters?

### 1.2 Design principles

1. **Local-first**  
   All core features must work locally without sending user data to a cloud service.

2. **Open formats**  
   `.ctxpack`, Context IR, eval reports, and plugin interfaces must be documented.

3. **Composable CLI-first design**  
   The CLI must feel like a serious developer tool, not a SaaS wrapper.

4. **Interoperability over lock-in**  
   Export to standard formats and existing ecosystems.

5. **Provenance by default**  
   Every chunk must be traceable back to its source document, section, page, or span.

6. **Security by default**  
  PII, secrets, prompt injection, and provenance/security findings must be first-class metadata. Permissions/ACL enforcement is a roadmap item, not a v0.1 guarantee.

7. **Evaluation as a core feature**  
   A context pipeline is not complete unless it can produce quality reports.

8. **Plugin architecture**  
   Contexte should not reimplement every parser or vector store. It should orchestrate and normalize.

9. **Determinism where possible**  
   Repeated builds with the same inputs and config should produce stable outputs.

10. **Graceful degradation**  
    Bad PDFs, unsupported formats, and low-confidence extraction should produce warnings, not silent corruption.

### 1.3 Non-goals

Contexte is **not**:

- a chatbot;
- a hosted SaaS product;
- a commercial platform;
- a full LangChain or LlamaIndex replacement;
- a vector database;
- a model provider;
- an agent framework;
- a PDF parser only;
- a proprietary ingestion pipeline;
- a no-code RAG builder.

Contexte should integrate with those tools, not compete directly with them.

---

## 2. Target Users and Use Cases

### 2.1 Primary users

#### AI engineer

Needs reproducible context pipelines, evals, chunking, source traceability, and exports.

#### Backend developer

Needs a simple CLI and SDK to convert documents into usable RAG data.

#### Research scientist

Needs experiments comparing chunking, retrieval, faithfulness, citations, compression, and context quality.

#### Open-source maintainer

Needs a neutral format and tooling for AI context.

#### Security/compliance engineer

Needs PII detection, secret detection, provenance, and a clear roadmap toward ACL metadata and policy controls.

### 2.2 Key use cases

#### Use case A — RAG readiness assessment

```bash
ctx probe ./company-docs
ctx build ./company-docs --to company.ctxpack --report
ctx eval company.ctxpack
```

Expected result:

- Count files by type.
- Detect unreadable files.
- Detect duplicated documents.
- Detect stale documents.
- Detect missing metadata.
- Detect PII/secrets.
- Estimate chunkability.
- Estimate citation coverage.
- Produce actionable recommendations.

#### Use case B — Build a portable context pack

```bash
ctx build ./docs --to docs.ctxpack
```

Expected result:

- Parse sources.
- Normalize content.
- Build Context IR.
- Create chunks.
- Preserve provenance.
- Save portable `.ctxpack`.

#### Use case C — Export to RAG JSONL

```bash
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
```

Expected result:

Each line should contain:

```json
{
  "id": "chunk_...",
  "text": "...",
  "metadata": {
    "source_uri": "...",
    "title": "...",
    "page": 3,
    "section": "..."
  }
}
```

#### Use case D — Future read-only serving adapters

```bash
ctx serve docs.ctxpack --http --read-only --port 8787
ctx serve docs.ctxpack --mcp --read-only --port 8787
```

This is optional and non-central. Contexte must remain MCP-compatible but MCP-independent.

Expected tools/resources:

- `search_context`
- `get_chunk`
- `get_source_metadata`
- `get_manifest`
- `explain_provenance`

#### Use case E — Evaluate context quality

```bash
ctx eval docs.ctxpack --suite basic --report eval.html
```

Expected metrics:

- Parse success rate.
- Chunk count.
- Average chunk length.
- Empty chunk ratio.
- Duplicate chunk ratio.
- Citation coverage.
- PII findings.
- Secret findings.
- Staleness warnings.
- Low-confidence extraction warnings.

---

## 3. MVP Scope

### 3.1 MVP objective

The MVP must reliably transform a local folder of documents into a `.ctxpack` with chunks, provenance, and a basic report.

### 3.2 MVP input formats

Required for v0.1:

- `.md`
- `.txt`
- `.html`
- `.pdf`
- `.docx`
- `.csv`
- `.json`

Optional for v0.2+:

- `.pptx`
- `.xlsx`
- `.eml`
- `.ipynb`
- source code repositories
- GitHub issues
- Slack exports
- Notion exports
- Google Drive exports

### 3.3 MVP output formats

Required for v0.1:

- `.ctxpack`
- JSONL chunks
- Markdown normalized output
- HTML report
- JSON report

Required for v0.2:

- LlamaIndex export
- LangChain export
- local HTTP read-only adapter
- stabilized plugin API

Required for v0.3:

- experimental MCP read-only adapter
- MCP security scanner
- tool description sanitizer
- server manifest signing

### 3.4 MVP core commands

Required:

```bash
ctx probe <path>
ctx build <path> --to <output.ctxpack>
ctx inspect <input.ctxpack>
ctx eval <input.ctxpack>
ctx export <input.ctxpack> --to jsonl --output <chunks.jsonl>
ctx report <input.ctxpack> --output <report.html>
```

Optional but desirable:

```bash
ctx diff old.ctxpack new.ctxpack
ctx serve input.ctxpack --http --read-only
ctx serve input.ctxpack --mcp --read-only
ctx validate input.ctxpack
ctx plugins list
```

### 3.5 MVP security

Required:

- Secret detection by regex.
- Basic PII detection by regex.
- Prompt injection heuristic scanner.
- Security findings attached to document and chunk metadata.

Do not require complex ML-based detection in v0.1.

---

## 4. Recommended Technology Stack

### 4.1 Primary language

Use **Python** for v0.1.

Reasons:

- rich document processing ecosystem;
- easy CLI development;
- easy Pydantic models;
- good support for AI/RAG tooling;
- quick open-source contribution path.

Future performance-critical modules may be rewritten in Rust.

### 4.2 Python version

Use Python `>=3.11`.

### 4.3 Recommended dependencies

Core:

```text
typer
rich
pydantic
pydantic-settings
orjson
python-slugify
platformdirs
tqdm
```

Document parsing:

```text
beautifulsoup4
markdown-it-py
pypdf
python-docx
pandas
```

Optional plugin integrations:

```text
docling
unstructured
apache-tika
presidio-analyzer
presidio-anonymizer
qdrant-client
fastapi
uvicorn
mcp
```

Testing:

```text
pytest
pytest-cov
hypothesis
ruff
mypy
types-python-dateutil
```

Packaging:

```text
uv
hatchling
```

Documentation:

```text
mkdocs
mkdocs-material
```

### 4.4 Avoid in core v0.1

Avoid mandatory dependencies on:

- cloud APIs;
- model providers;
- GPU libraries;
- heavyweight OCR;
- vector databases;
- Java services;
- SaaS-specific SDKs.

Keep the core install lightweight.

---

## 5. Repository Structure

Recommended monorepo:

```text
contexte/
  README.md
  LICENSE
  pyproject.toml
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  SECURITY.md
  CHANGELOG.md

  docs/
    index.md
    getting-started.md
    cli.md
    concepts/
      context-ir.md
      ctxpack.md
      chunking.md
      provenance.md
      security.md
      evaluation.md
    rfc/
      0001-context-ir.md
      0002-ctxpack.md
      0003-plugin-api.md

  src/
    contexte/
      __init__.py
      cli/
        __init__.py
        app.py
        commands/
          probe.py
          build.py
          inspect.py
          eval.py
          export.py
          report.py
          validate.py
          serve.py
      core/
        pipeline.py
        config.py
        errors.py
        logging.py
        ids.py
        hashing.py
      ir/
        models.py
        schema.py
        validate.py
        serialize.py
      pack/
        writer.py
        reader.py
        manifest.py
        layout.py
      decoders/
        base.py
        registry.py
        text.py
        markdown.py
        html.py
        pdf.py
        docx.py
        csv.py
        json.py
      normalizers/
        text.py
        metadata.py
        dedupe.py
      chunkers/
        base.py
        fixed.py
        heading.py
        semantic_placeholder.py
      security/
        pii.py
        secrets.py
        prompt_injection.py
        policy.py
      eval/
        metrics.py
        suite_basic.py
        report.py
      exporters/
        base.py
        jsonl.py
        markdown.py
        llamaindex.py
        langchain.py
      mcp/
        server.py
        tools.py
      plugins/
        api.py
        loader.py

  tests/
    fixtures/
      docs/
      packs/
    unit/
    integration/
    e2e/

  examples/
    quickstart/
    local-docs-to-ctxpack/
    ctxpack-to-jsonl/
    docs-to-mcp/

  benchmarks/
    README.md
    corpora/
    expected/
    metrics/

  scripts/
    generate_schema.py
    release_check.py
```

---

## 6. Core Concepts

### 6.1 Source

A source is any input object:

- file;
- directory;
- URL export;
- database dump;
- conversation export;
- repository;
- API result.

In v0.1, source means local files and directories.

### 6.2 Decoder

A decoder transforms a source file into Context IR documents.

Example:

```text
PDF file -> Document with blocks, metadata, pages, spans
```

### 6.3 Context IR

Context IR is the canonical intermediate representation.

It represents documents, blocks, chunks, provenance, security labels, extraction confidence, and lineage.

### 6.4 Chunk

A chunk is a retrieval-ready unit of context derived from one or more blocks.

A chunk must have:

- stable ID;
- text;
- source references;
- metadata;
- security labels;
- optional embedding metadata;
- optional quality metrics.

### 6.5 Context Pack

A `.ctxpack` is a portable archive containing:

- manifest;
- documents;
- chunks;
- sources metadata;
- eval reports;
- security findings;
- pipeline config;
- checksums.

### 6.6 Eval report

An eval report describes the quality and safety of a context pack.

It should be both machine-readable and human-readable.

---

## 7. Context IR Specification

### 7.1 Design requirements

The IR must be:

- JSON-serializable;
- versioned;
- easy to validate;
- stable across releases;
- extensible;
- suitable for local processing;
- able to preserve provenance;
- able to represent partial extraction failures.

### 7.2 Top-level document model

Python/Pydantic target model:

```python
class ContextDocument(BaseModel):
    id: str
    schema_version: str
    source: SourceRef
    title: str | None = None
    language: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    extracted_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    blocks: list[Block]
    security: SecuritySummary = Field(default_factory=SecuritySummary)
    lineage: Lineage
    errors: list[ExtractionError] = Field(default_factory=list)
```

### 7.3 SourceRef

```python
class SourceRef(BaseModel):
    uri: str
    type: str
    media_type: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None
    original_path: str | None = None
```

### 7.4 Block

A block is the smallest structured unit extracted from a document.

```python
class Block(BaseModel):
    id: str
    type: Literal[
        "title",
        "heading",
        "paragraph",
        "list",
        "list_item",
        "table",
        "image",
        "code",
        "quote",
        "footnote",
        "page_break",
        "metadata",
        "unknown"
    ]
    text: str | None = None
    markdown: str | None = None
    html: str | None = None
    level: int | None = None
    page: int | None = None
    bbox: BoundingBox | None = None
    source_span: SourceSpan | None = None
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = None
```

### 7.5 SourceSpan

```python
class SourceSpan(BaseModel):
    start: int | None = None
    end: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    page_start: int | None = None
    page_end: int | None = None
```

### 7.6 BoundingBox

```python
class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float
    coordinate_system: str = "page"
```

### 7.7 Lineage

```python
class Lineage(BaseModel):
    decoder: str
    decoder_version: str | None = None
    pipeline_version: str
    pipeline_config_hash: str
    created_by: str = "contexte"
```

### 7.8 SecuritySummary

```python
class SecuritySummary(BaseModel):
    pii_count: int = 0
    secret_count: int = 0
    prompt_injection_score: float | None = None
    labels: list[str] = Field(default_factory=list)
```

### 7.9 ExtractionError

```python
class ExtractionError(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "error", "critical"]
    location: str | None = None
```

---

## 8. Chunk Model Specification

### 8.1 Chunk model

```python
class ContextChunk(BaseModel):
    id: str
    schema_version: str
    document_id: str
    text: str
    title: str | None = None
    section_path: list[str] = Field(default_factory=list)
    source_refs: list[ChunkSourceRef]
    token_count_estimate: int | None = None
    char_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    security: ChunkSecurity = Field(default_factory=ChunkSecurity)
    quality: ChunkQuality = Field(default_factory=ChunkQuality)
```

### 8.2 ChunkSourceRef

```python
class ChunkSourceRef(BaseModel):
    document_id: str
    block_ids: list[str]
    source_uri: str
    page_start: int | None = None
    page_end: int | None = None
    line_start: int | None = None
    line_end: int | None = None
```

### 8.3 ChunkSecurity

```python
class ChunkSecurity(BaseModel):
    pii_count: int = 0
    secret_count: int = 0
    prompt_injection_score: float | None = None
    labels: list[str] = Field(default_factory=list)
    allowed_groups: list[str] = Field(default_factory=list)
```

### 8.4 ChunkQuality

```python
class ChunkQuality(BaseModel):
    extraction_confidence: float | None = None
    chunk_coherence_score: float | None = None
    duplicate_score: float | None = None
    has_citation: bool = False
    warnings: list[str] = Field(default_factory=list)
```

### 8.5 Stable IDs

Document IDs should be generated from source hash plus normalized URI:

```text
doc_<first_16_chars_sha256>
```

Block IDs:

```text
blk_<document_short_id>_<zero_padded_index>
```

Chunk IDs:

```text
chk_<document_short_id>_<chunk_strategy>_<zero_padded_index>
```

If content changes, IDs may change. If only metadata changes, IDs should remain stable where possible.

---

## 9. `.ctxpack` Specification

### 9.1 Format

A `.ctxpack` is a ZIP archive with a deterministic internal layout.

Required layout:

```text
example.ctxpack
  manifest.json
  documents/
    documents.jsonl
  chunks/
    chunks.jsonl
  reports/
    build-report.json
  security/
    findings.jsonl
  metadata/
    sources.jsonl
    pipeline.json
    checksums.json
```

Optional layout:

```text
  normalized/
    markdown/
      <document_id>.md
  eval/
    basic-report.json
    basic-report.html
  embeddings/
    embeddings.parquet
  indexes/
    qdrant/
    pgvector/
  original/
    ...
```

### 9.2 Manifest schema

```json
{
  "schema_version": "0.1.0",
  "pack_id": "ctxpack_...",
  "created_at": "2026-04-29T00:00:00Z",
  "created_by": "contexte",
  "contexte_version": "0.1.0",
  "source_summary": {
    "source_root": "./docs",
    "document_count": 12,
    "chunk_count": 142
  },
  "features": {
    "has_documents": true,
    "has_chunks": true,
    "has_security_findings": true,
    "has_eval": false,
    "has_embeddings": false
  },
  "checksums": {
    "documents/documents.jsonl": "sha256:...",
    "chunks/chunks.jsonl": "sha256:..."
  }
}
```

### 9.3 Requirements

The pack writer must:

- create deterministic paths;
- include schema version;
- include checksums;
- fail on invalid JSON;
- validate all documents and chunks before writing;
- write atomically to avoid corrupt packs.

The pack reader must:

- validate manifest exists;
- validate schema compatibility;
- validate checksums unless `--skip-checksums`;
- stream JSONL files when possible;
- expose document and chunk iterators.

---

## 10. CLI Specification

### 10.1 CLI UX

Use Typer + Rich.

All commands should support:

```bash
--help
--verbose
--quiet
--json
```

Where useful:

```bash
--config contexte.yaml
--output <path>
--force
```

### 10.2 `ctx probe`

Purpose: inspect files before building.

```bash
ctx probe ./docs
ctx probe ./docs --json
```

Output:

- file count;
- file types;
- supported/unsupported;
- total size;
- likely decoder;
- warnings.

Acceptance criteria:

- Works on file or directory.
- Does not create a pack.
- Exits non-zero only on fatal path errors.

### 10.3 `ctx build`

Purpose: build `.ctxpack`.

```bash
ctx build ./docs --to docs.ctxpack
```

Options:

```bash
--to <path>
--chunker heading|fixed
--max-chars <int>
--include <glob>
--exclude <glob>
--report
--force
```

Acceptance criteria:

- Creates a valid `.ctxpack`.
- Includes documents and chunks.
- Includes build report.
- Skips unsupported files with warnings.
- Does not silently swallow fatal decoder errors.

### 10.4 `ctx inspect`

Purpose: display pack summary.

```bash
ctx inspect docs.ctxpack
ctx inspect docs.ctxpack --json
```

Output:

- pack ID;
- schema version;
- created at;
- document count;
- chunk count;
- security findings count;
- eval availability;
- top warnings.

### 10.5 `ctx eval`

Purpose: evaluate pack.

```bash
ctx eval docs.ctxpack
ctx eval docs.ctxpack --report eval.html
```

Metrics:

- document count;
- chunk count;
- empty chunks;
- average chunk char length;
- chunks without citations;
- duplicate chunk ratio;
- PII findings;
- secret findings;
- prompt injection warnings;
- extraction errors.

### 10.6 `ctx export`

Purpose: export pack.

```bash
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
ctx export docs.ctxpack --to markdown --output normalized/
```

MVP supports:

- `jsonl`
- `markdown`

### 10.7 `ctx report`

Purpose: generate human-readable report.

```bash
ctx report docs.ctxpack --output report.html
```

### 10.8 `ctx validate`

Purpose: validate pack and schema.

```bash
ctx validate docs.ctxpack
```

Checks:

- manifest exists;
- JSONL valid;
- checksums valid;
- schema versions supported;
- required files present.

### 10.9 `ctx serve`

Purpose: expose a pack through future optional read-only HTTP or MCP adapters.

v0.1 behavior is a placeholder only; serving must not be a core dependency.

```bash
ctx serve docs.ctxpack --http --read-only --port 8787
ctx serve docs.ctxpack --mcp --read-only --port 8787
```

---

## 11. Pipeline Specification

### 11.1 Default build pipeline

```text
1. Resolve input path.
2. Discover files recursively.
3. Filter files by include/exclude globs.
4. Hash files.
5. Pick decoder per file.
6. Decode into ContextDocument.
7. Normalize text and metadata.
8. Run security scanners.
9. Chunk documents.
10. Compute chunk quality metadata.
11. Build reports.
12. Write ctxpack.
13. Validate ctxpack.
```

### 11.2 Pipeline config file

Support `contexte.yaml`:

```yaml
schema_version: "0.1"

input:
  include:
    - "**/*.md"
    - "**/*.txt"
    - "**/*.html"
    - "**/*.pdf"
    - "**/*.docx"
  exclude:
    - "**/.git/**"
    - "**/node_modules/**"
    - "**/dist/**"

chunking:
  strategy: heading
  max_chars: 3000
  overlap_chars: 200

security:
  pii: true
  secrets: true
  prompt_injection: true

output:
  pack: docs.ctxpack
  report: report.html
```

### 11.3 Error handling

Use structured errors.

Fatal errors:

- input path does not exist;
- output exists and `--force` not provided;
- cannot write output;
- invalid config;
- corrupted pack on validation.

Non-fatal warnings:

- unsupported file;
- decoder failed for one file;
- empty document;
- low confidence extraction;
- possible PII;
- possible prompt injection.

---

## 12. Decoder Specification

### 12.1 Base interface

```python
class Decoder(Protocol):
    id: str
    supported_extensions: set[str]
    supported_media_types: set[str]

    def can_decode(self, source: SourceRef) -> bool:
        ...

    def decode(self, path: Path, context: DecodeContext) -> ContextDocument:
        ...
```

### 12.2 Text decoder

For `.txt`.

Rules:

- read UTF-8;
- fallback to detected encoding if needed;
- split by paragraphs;
- create paragraph blocks;
- preserve line spans if possible.

### 12.3 Markdown decoder

For `.md`.

Rules:

- parse headings;
- preserve code blocks;
- preserve list items;
- create section hierarchy;
- create heading and paragraph blocks.

### 12.4 HTML decoder

For `.html`.

Rules:

- use BeautifulSoup;
- remove scripts/styles;
- extract title;
- preserve headings;
- preserve links in metadata;
- convert tables to Markdown where possible.

### 12.5 PDF decoder

For `.pdf`.

MVP rules:

- use `pypdf`;
- extract text per page;
- create page-aware paragraph blocks;
- record page number;
- if no text found, warn `pdf_no_text_extracted`;
- do not require OCR in v0.1.

Future:

- Docling plugin;
- OCR plugin;
- table extraction plugin.

### 12.6 DOCX decoder

For `.docx`.

Rules:

- use `python-docx`;
- extract paragraphs;
- detect headings from styles;
- extract tables into Markdown;
- preserve paragraph order.

### 12.7 CSV decoder

For `.csv`.

Rules:

- use pandas or csv module;
- create metadata summary;
- create Markdown table preview;
- for large CSVs, do not dump entire file into one chunk;
- create row-group blocks.

### 12.8 JSON decoder

For `.json`.

Rules:

- validate JSON;
- pretty-print compactly;
- create code block or structured text block;
- for arrays of objects, produce grouped blocks.

---

## 13. Normalization Specification

### 13.1 Text normalization

Functions:

- normalize Unicode;
- normalize whitespace;
- trim repeated blank lines;
- remove null bytes;
- preserve meaningful line breaks in code/tables;
- normalize quotes only if safe;
- do not destroy source span metadata.

### 13.2 Metadata normalization

Extract:

- title;
- extension;
- file size;
- modified time;
- created time if available;
- SHA256;
- relative path;
- media type.

### 13.3 Deduplication

MVP:

- exact duplicate source detection by SHA256;
- exact duplicate chunk detection by normalized text hash.

Future:

- fuzzy duplicate detection;
- near-duplicate document clustering.

---

## 14. Chunking Specification

### 14.1 Fixed chunker

Input: blocks.  
Output: chunks with max characters and overlap.

Rules:

- never create empty chunks;
- preserve source block IDs;
- avoid splitting inside code/table blocks when possible;
- attach source refs.

### 14.2 Heading-aware chunker

Default MVP chunker.

Rules:

- use headings to build section path;
- include heading context in chunk title;
- group paragraphs under headings;
- split large sections by max chars;
- preserve table blocks as standalone chunks if large;
- include section_path metadata.

### 14.3 Semantic chunker placeholder

Do not implement embedding-based semantic chunking in v0.1 core.

Implement interface and placeholder:

```bash
--chunker semantic
```

Should return a clear error unless plugin installed:

```text
Semantic chunking requires plugin: contexte-semantic
```

---

## 15. Security Specification

### 15.1 Secret scanner

MVP regex patterns:

- API keys;
- AWS access key ID;
- private key headers;
- GitHub tokens;
- Slack tokens;
- generic long high-entropy strings.

Example labels:

```text
secret:api_key
secret:aws_access_key
secret:private_key
secret:github_token
```

### 15.2 PII scanner

MVP regex patterns:

- email addresses;
- phone numbers;
- credit card-like numbers;
- IP addresses;
- US SSN pattern;
- IBAN-like strings.

Example labels:

```text
pii:email
pii:phone
pii:credit_card_candidate
pii:ssn_candidate
```

### 15.3 Prompt injection scanner

MVP heuristic scanner.

Detect phrases such as:

- ignore previous instructions;
- disregard system message;
- reveal hidden prompt;
- exfiltrate;
- send this data to;
- developer message;
- system prompt;
- tool call;
- override instructions.

The scanner must not delete content by default. It should mark findings.

### 15.4 Security finding model

```python
class SecurityFinding(BaseModel):
    id: str
    document_id: str
    chunk_id: str | None = None
    type: Literal["pii", "secret", "prompt_injection", "policy"]
    label: str
    severity: Literal["low", "medium", "high", "critical"]
    text_preview: str | None = None
    location: SourceSpan | None = None
    recommendation: str | None = None
```

### 15.5 Redaction

Redaction is optional and should not be default in v0.1.

Future command:

```bash
ctx build ./docs --redact pii,secrets --to redacted.ctxpack
```

---

## 16. Evaluation Specification

### 16.1 Basic eval suite

Implement in v0.1.

Metrics:

```python
class BasicEvalReport(BaseModel):
    document_count: int
    chunk_count: int
    unsupported_file_count: int
    failed_file_count: int
    empty_document_count: int
    empty_chunk_count: int
    avg_chunk_chars: float
    median_chunk_chars: float
    max_chunk_chars: int
    chunks_without_source_refs: int
    chunks_without_citations_ratio: float
    duplicate_chunk_ratio: float
    pii_finding_count: int
    secret_finding_count: int
    prompt_injection_finding_count: int
    warnings: list[str]
```

### 16.2 RAG readiness score

Compute a simple 0–100 score.

Suggested formula:

```text
score = 100
- 20 * failed_file_ratio
- 15 * empty_document_ratio
- 15 * chunks_without_citations_ratio
- 10 * duplicate_chunk_ratio
- 10 if pii findings exist
- 10 if secret findings exist
- 10 if many unsupported files
- 10 if avg chunk length outside recommended range
```

Clamp between 0 and 100.

Explain the score. Do not present it as scientific truth or as a guarantee of RAG performance.

### 16.3 HTML report sections

Required:

- Executive summary.
- Input summary.
- Document parsing summary.
- Chunking summary.
- Security findings summary.
- Quality metrics.
- Top warnings.
- Recommended next actions.

---

## 17. Export Specification

### 17.1 JSONL export

Each line:

```json
{
  "id": "chk_...",
  "text": "...",
  "metadata": {
    "document_id": "doc_...",
    "source_uri": "...",
    "title": "...",
    "section_path": ["..."],
    "page_start": 1,
    "page_end": 2
  }
}
```

### 17.2 Markdown export

Export normalized documents:

```text
normalized/
  doc_<id>.md
```

Each Markdown file should include YAML frontmatter:

```yaml
---
document_id: doc_...
source_uri: file:///...
title: Example
---
```

### 17.3 LlamaIndex export

v0.2 target.

Generate a JSONL or Python helper compatible with LlamaIndex `Document`.

### 17.4 LangChain export

v0.2 target.

Generate JSONL compatible with LangChain `Document` shape:

```json
{
  "page_content": "...",
  "metadata": {}
}
```

---

## 18. Read-only MCP Adapter Specification

MCP support is optional, experimental, and not part of the v0.1 trust core.

Contexte must never require MCP. MCP support is an optional serving adapter, not a core dependency.

The default MCP mode must be read-only. No write tools. No shell execution. No network access unless explicitly enabled in a future release.

### 18.1 Tools

#### `search_context`

Input:

```json
{
  "query": "remote work policy",
  "limit": 10
}
```

Output:

```json
{
  "results": [
    {
      "chunk_id": "chk_...",
      "text": "...",
      "score": 0.82,
      "source": {
        "uri": "...",
        "page": 3,
        "section": "Remote Work"
      }
    }
  ]
}
```

For MVP, lexical search is acceptable.

#### `get_chunk`

Input:

```json
{
  "chunk_id": "chk_..."
}
```

#### `get_source_metadata`

Input:

```json
{
  "document_id": "doc_..."
}
```

#### `explain_provenance`

Input:

```json
{
  "chunk_id": "chk_..."
}
```

#### `get_manifest`

Input:

```json
{}
```

### 18.2 Search

MVP MCP search can use:

- lowercase token matching;
- BM25 optional;
- no embeddings required.

Future:

- vector search;
- hybrid search;
- ACL-aware retrieval.

---

## 19. Plugin Architecture

### 19.1 Plugin goals

Plugins allow optional integrations without bloating core.

Plugin categories:

- decoders;
- chunkers;
- security scanners;
- exporters;
- vector stores;
- future read-only MCP tools/adapters;
- eval suites.

### 19.2 Plugin interface

```python
class ContextePlugin(Protocol):
    id: str
    version: str

    def register(self, registry: PluginRegistry) -> None:
        ...
```

### 19.3 Registry

```python
class PluginRegistry:
    def register_decoder(self, decoder: Decoder) -> None: ...
    def register_chunker(self, chunker: Chunker) -> None: ...
    def register_exporter(self, exporter: Exporter) -> None: ...
    def register_eval_suite(self, suite: EvalSuite) -> None: ...
```

### 19.4 Discovery

Use Python entry points:

```toml
[project.entry-points."contexte.plugins"]
docling = "contexte_docling:Plugin"
qdrant = "contexte_qdrant:Plugin"
```

---

## 20. Configuration and Versioning

### 20.1 Semantic versioning

Use SemVer:

```text
MAJOR.MINOR.PATCH
```

### 20.2 Schema versioning

Context IR and `.ctxpack` schema versions must be independent from package version.

Example:

```text
contexte version: 0.1.0
context_ir_schema: 0.1.0
ctxpack_schema: 0.1.0
```

### 20.3 Backward compatibility

Before v1.0:

- breaking changes allowed but must be documented.

After v1.0:

- readers should support at least the previous major version;
- migration tools should be provided.

---

## 21. Testing Requirements

### 21.1 Unit tests

Required coverage:

- ID generation;
- hashing;
- each decoder;
- normalization;
- chunkers;
- pack writer;
- pack reader;
- validation;
- security scanners;
- eval metrics;
- exporters.

### 21.2 Integration tests

Required:

- build `.ctxpack` from fixture directory;
- inspect generated pack;
- export to JSONL;
- validate pack;
- generate report.

### 21.3 End-to-end test

Command:

```bash
ctx build tests/fixtures/docs --to /tmp/test.ctxpack --report
ctx validate /tmp/test.ctxpack
ctx inspect /tmp/test.ctxpack --json
ctx export /tmp/test.ctxpack --to jsonl --output /tmp/chunks.jsonl
ctx eval /tmp/test.ctxpack --report /tmp/eval.html
```

### 21.4 Fixture documents

Create fixtures:

```text
simple.md
simple.txt
simple.html
simple.docx
simple.pdf
table.csv
data.json
contains_email.txt
contains_secret.txt
prompt_injection.txt
duplicate_a.md
duplicate_b.md
```

### 21.5 Quality gates

CI must run:

```bash
ruff check .
ruff format --check .
mypy src
pytest --cov=contexte
```

Minimum coverage for v0.1:

```text
75%
```

Target for v1.0:

```text
90%
```

---

## 22. Documentation Requirements

### 22.1 README structure

README must include:

- project description;
- install;
- quickstart;
- core concepts;
- CLI examples;
- output examples;
- status warning;
- roadmap;
- contribution link;
- license.

### 22.2 Quickstart

```bash
pip install contexte
ctx build ./docs --to docs.ctxpack --report
ctx inspect docs.ctxpack
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
```

### 22.3 Developer docs

Must include:

- architecture overview;
- Context IR spec;
- `.ctxpack` spec;
- plugin API;
- contribution guide;
- testing guide;
- release guide.

---

## 23. Security Policy

### 23.1 SECURITY.md

Include:

- supported versions;
- vulnerability reporting process;
- disclosure policy;
- security scope.

### 23.2 Sensitive data policy

Contexte must never upload data by default.

If future plugins call external APIs, they must require explicit opt-in and clear documentation.

### 23.3 Safe defaults

Default behavior:

- local processing only;
- no telemetry;
- no cloud calls;
- no embeddings API;
- no sending documents to any remote service.

---

## 24. Open Source Governance

### 24.1 License

Use Apache-2.0.

### 24.2 Required files

```text
LICENSE
README.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
SECURITY.md
CHANGELOG.md
```

### 24.3 Contribution model

Use GitHub pull requests.

Require:

- tests for new features;
- docs for new user-facing behavior;
- changelog entry for significant changes.

### 24.4 RFC process

Use `docs/rfc`.

RFCs required for:

- Context IR breaking changes;
- `.ctxpack` schema changes;
- plugin API changes;
- security model changes;
- major CLI changes.

---

## 25. Implementation Plan for Codex/GPT-5.5

This section is written directly for an AI coding agent.

### 25.1 Objective

Implement a working v0.1 of Contexte as a Python package with a CLI named `ctx`.

### 25.2 Do not overbuild

Do not implement:

- cloud sync;
- vector DB integrations;
- real embeddings;
- OCR;
- full MCP unless MVP is complete;
- GUI;
- SaaS backend;
- complex semantic chunking.

### 25.3 Build order

Implement in this exact order:

1. Project skeleton.
2. Pydantic IR models.
3. Source discovery and hashing.
4. Basic decoders: txt, md, html.
5. Pack writer/reader.
6. Fixed chunker.
7. `ctx build`.
8. `ctx inspect`.
9. `ctx validate`.
10. JSONL export.
11. Basic eval metrics.
12. HTML report.
13. PDF decoder.
14. DOCX decoder.
15. CSV decoder.
16. JSON decoder.
17. Heading-aware chunker.
18. Security scanners.
19. Tests and fixtures.
20. Documentation.

### 25.4 Implementation detail: project skeleton

Use `pyproject.toml`.

Expected package:

```text
src/contexte
```

Expose CLI:

```toml
[project.scripts]
ctx = "contexte.cli.app:app"
```

### 25.5 Implementation detail: Pydantic models

Create models in:

```text
src/contexte/ir/models.py
```

All models must be serializable to JSON.

Use `model_config = ConfigDict(extra="allow")` only where extension fields are intended.

### 25.6 Implementation detail: pack writer

Write to temporary directory first:

```text
<output>.tmp/
```

Then ZIP into final `.ctxpack`.

If final exists and `--force` is false, error.

### 25.7 Implementation detail: reports

Generate JSON first.

HTML can be simple static HTML. No external assets required.

### 25.8 Implementation detail: CLI output

Use Rich tables for human output.

For `--json`, output machine-readable JSON only.

### 25.9 Implementation detail: tests

Use fixtures and ensure tests run offline.

Do not require internet access for tests.

---

## 26. Acceptance Criteria for v0.1

A maintainer should be able to run:

```bash
pip install -e ".[dev]"
ctx build examples/quickstart/docs --to /tmp/quickstart.ctxpack --report --force
ctx validate /tmp/quickstart.ctxpack
ctx inspect /tmp/quickstart.ctxpack
ctx eval /tmp/quickstart.ctxpack --report /tmp/eval.html
ctx export /tmp/quickstart.ctxpack --to jsonl --output /tmp/chunks.jsonl
```

And observe:

- valid `.ctxpack`;
- non-empty documents;
- non-empty chunks;
- manifest present;
- checksums valid;
- JSONL export present;
- report generated;
- tests passing.

### 26.1 Required `ctx inspect` example output

```text
Contexte Pack

Path: /tmp/quickstart.ctxpack
Schema: 0.1.0
Documents: 6
Chunks: 24
Security findings: 2
Build warnings: 1
```

### 26.2 Required `ctx eval` example output

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

---

## 27. Example README Draft

```md
# Contexte

Contexte is an open-source toolkit for compiling raw documents,
repositories, and data sources into trustworthy AI context.

It provides:

- a CLI named `ctx`
- a portable `.ctxpack` format
- a Context IR specification
- document ingestion and normalization
- chunking with provenance
- security checks for PII, secrets, and prompt injection
- RAG readiness reports
- exports to JSONL, Markdown, and future RAG frameworks

## Install

```bash
pip install contexte
```

## Quickstart

```bash
ctx build ./docs --to docs.ctxpack --report
ctx inspect docs.ctxpack
ctx eval docs.ctxpack
ctx export docs.ctxpack --to jsonl --output chunks.jsonl
```

## Why?

AI systems do not only need better models.
They need better context.

Contexte helps transform messy raw data into context that is portable,
auditable, citable, and ready for retrieval or agent workflows.
```

---

## 28. Example `contexte.yaml`

```yaml
schema_version: "0.1"

input:
  include:
    - "**/*.md"
    - "**/*.txt"
    - "**/*.html"
    - "**/*.pdf"
    - "**/*.docx"
    - "**/*.csv"
    - "**/*.json"
  exclude:
    - "**/.git/**"
    - "**/node_modules/**"
    - "**/dist/**"
    - "**/__pycache__/**"

chunking:
  strategy: heading
  max_chars: 3000
  overlap_chars: 200

security:
  pii: true
  secrets: true
  prompt_injection: true

report:
  html: true
  json: true
```

---

## 29. Future Roadmap

### v0.1 — Local context compiler

- CLI.
- Context IR.
- `.ctxpack`.
- Basic decoders.
- Basic chunking.
- Basic eval.
- Basic security scanning.
- JSONL/Markdown exports.

### v0.2 — Interoperability

- LlamaIndex export.
- LangChain export.
- Plugin API stabilized.
- Local HTTP read-only server.
- Better decoder integrations.

### v0.3 — Optional MCP adapter

- MCP read-only adapter (experimental).
- MCP security scanner.
- Server manifest signing.
- Tool description sanitizer.

### v0.4 — Better document intelligence and governance

- Docling plugin.
- Unstructured plugin.
- OCR plugin.
- Table-aware chunking.
- Code-aware chunking.
- Better PDF layout preservation.
- Better PII detection.
- Presidio plugin.
- ACL metadata support.
- Policy engine.
- Pack signing.
- Tamper detection.

### v0.5 — Evaluation and benchmarks

- Public benchmark scaffold.
- ContextBench fixtures.
- Retrieval eval generation.
- Citation faithfulness.
- Stale document detection.
- Conflict detection.
- Chunk quality scoring.

### v1.0 — Stable standard

- Stable Context IR.
- Stable `.ctxpack`.
- Stable plugin API.
- Migration tools.
- Production-ready docs.
- Broad ecosystem integrations.

---

## 30. Important Product Decisions

### 30.1 Keep `ctx` as CLI name

Even if the project is named Contexte, developers should type `ctx`.

### 30.2 Keep `.ctxpack` as portable output

The `.ctxpack` is central. It gives the project a standard artifact.

### 30.3 Do not require embeddings

Embeddings are useful, but not required for context compilation.

### 30.4 Treat citations as mandatory

Chunks without provenance are low-quality chunks.

### 30.5 Treat reports as first-class

The report is one of the most valuable outputs.

### 30.6 Avoid vendor-specific defaults

No default dependency on OpenAI, Anthropic, Google, Pinecone, or any SaaS.

### 30.7 Prefer adapters over replacements

Use plugins to integrate existing best-in-class tools.

---

## 31. Development Checklist

### Project setup

- [ ] Create Python package.
- [ ] Add Apache-2.0 license.
- [ ] Add CLI entrypoint.
- [ ] Add Ruff.
- [ ] Add MyPy.
- [ ] Add Pytest.
- [ ] Add GitHub Actions.

### Core

- [ ] Define IR models.
- [ ] Define chunk models.
- [ ] Define security finding model.
- [ ] Define manifest model.
- [ ] Implement hashing.
- [ ] Implement source discovery.

### Decoders

- [ ] Text.
- [ ] Markdown.
- [ ] HTML.
- [ ] PDF.
- [ ] DOCX.
- [ ] CSV.
- [ ] JSON.

### Chunking

- [ ] Fixed chunker.
- [ ] Heading-aware chunker.
- [ ] Chunk source refs.
- [ ] Chunk metadata.

### Pack

- [ ] Writer.
- [ ] Reader.
- [ ] Checksum generation.
- [ ] Validation.

### CLI

- [ ] `ctx probe`
- [ ] `ctx build`
- [ ] `ctx inspect`
- [ ] `ctx validate`
- [ ] `ctx eval`
- [ ] `ctx export`
- [ ] `ctx report`

### Security

- [ ] PII regex scanner.
- [ ] Secret regex scanner.
- [ ] Prompt injection scanner.
- [ ] Findings JSONL.

### Reports

- [ ] Build report JSON.
- [ ] Eval report JSON.
- [ ] HTML report.

### Tests

- [ ] Unit tests.
- [ ] Integration tests.
- [ ] E2E test.
- [ ] Fixture docs.

### Docs

- [ ] README.
- [ ] Getting started.
- [ ] CLI docs.
- [ ] Context IR spec.
- [ ] `.ctxpack` spec.
- [ ] Plugin API.

---

## 32. Definition of Done for Initial Release

The initial open-source release is done when:

1. A new user can install the package locally.
2. The `ctx` command works.
3. A folder of sample docs can be converted into `.ctxpack`.
4. The `.ctxpack` validates.
5. Chunks have provenance.
6. JSONL export works.
7. HTML report works.
8. Basic security findings work.
9. Tests pass in CI.
10. Documentation explains the project clearly.
11. No cloud service is required.
12. The project is licensed Apache-2.0.

---

## 33. Final Instruction to the Coding Agent

Implement Contexte as a clean, tested, extensible Python open-source project.

Prioritize:

1. correctness;
2. simple architecture;
3. documented schemas;
4. deterministic local behavior;
5. useful CLI;
6. tests;
7. extensibility.

Do not over-optimize early.  
Do not build a SaaS.  
Do not hide data transformations.  
Do not create vendor lock-in.  
Do not require external APIs.

The first release should make this command work beautifully:

```bash
ctx build ./docs --to docs.ctxpack --report
```

And this should be true:

> A developer can trust that the generated context is structured, traceable, portable, and ready for AI workflows.
