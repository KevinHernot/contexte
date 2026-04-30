# Contributing

Thanks for helping build Contexte.

## Development setup

1. Create a Python 3.11+ virtual environment.
2. Install the project in editable mode with development dependencies.
3. Run the test and quality gates before opening a pull request.

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy src
pytest --cov=contexte
```

## Contribution expectations

- Keep core behavior local-first and deterministic where possible.
- Add tests for new behavior.
- Update docs for user-facing changes.
- Add a changelog entry for significant changes.
- Use RFCs in `docs/rfc/` for schema, pack, plugin, security, or major CLI changes.
