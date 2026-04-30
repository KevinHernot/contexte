# Plugin API

Plugins extend Contexte without bloating core.

Plugin categories:

- decoders;
- chunkers;
- exporters;
- eval suites;
- future vector stores and read-only MCP tools/adapters.

## Entry point

```toml
[project.entry-points."contexte.plugins"]
docling = "contexte_docling:Plugin"
```

## Interface

Plugins implement:

```python
class Plugin:
    id = "my-plugin"
    version = "0.1.0"

    def register(self, registry):
        registry.register_decoder(MyDecoder())
```

The v0.1 API is intentionally small and may evolve before v1.0.
