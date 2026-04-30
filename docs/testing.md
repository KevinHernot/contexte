# Testing

Run all quality gates:

```bash
ruff check .
ruff format --check .
mypy src
pytest --cov=contexte
```

The test suite is offline and uses fixtures under `tests/fixtures/docs`.

## Acceptance flow

```bash
ctx build tests/fixtures/docs --to /tmp/test.ctxpack --report --force
ctx validate /tmp/test.ctxpack
ctx inspect /tmp/test.ctxpack --json
ctx export /tmp/test.ctxpack --to jsonl --output /tmp/chunks.jsonl
ctx eval /tmp/test.ctxpack --report /tmp/eval.html
```
