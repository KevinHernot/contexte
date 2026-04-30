# ctxpack-to-jsonl

Build a pack, then export retrieval-ready chunks:

```bash
ctx build ../quickstart/docs --to /tmp/quickstart.ctxpack --force
ctx export /tmp/quickstart.ctxpack --to jsonl --output /tmp/chunks.jsonl
```
