# Getting started

## Install

```bash
pip install contexte
```

For development:

```bash
pip install -e ".[dev]"
```

## Build your first pack

```bash
ctx build examples/quickstart/docs --to /tmp/quickstart.ctxpack --report --force
ctx validate /tmp/quickstart.ctxpack
ctx inspect /tmp/quickstart.ctxpack
ctx eval /tmp/quickstart.ctxpack --report /tmp/eval.html
ctx export /tmp/quickstart.ctxpack --to jsonl --output /tmp/chunks.jsonl
```

## What you get

A `.ctxpack` contains:

- `manifest.json`
- normalized Context IR documents
- retrieval-ready chunks
- source metadata
- security findings
- build report
- checksums
