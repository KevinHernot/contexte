# Extension Policy

To ensure interoperability and avoid key collisions in Context IR, all extensions and plugins must follow this metadata namespacing policy.

## Metadata Namespacing

Metadata fields in `ContextDocument`, `Block`, and `ContextChunk` should use the following format:

`[namespace]:[plugin_id]:[key]`

### Standard Namespaces

| Namespace | Purpose |
| :--- | :--- |
| `core:` | Reserved for official Contexte core features. |
| `plugin:` | Used by optional plugins (e.g., `plugin:docling:table_structure`). |
| `user:` | Reserved for end-user custom metadata. |
| `ext:` | Used for experimental or third-party extensions not yet in the plugin registry. |

### Example

```json
{
  "metadata": {
    "plugin:docling:page_layout": "standard",
    "user:project_id": "SP-2026",
    "core:priority": 1
  }
}
```

## Plugin Registration

Plugins should declare their namespace upon registration. The `DecoderRegistry` and `ChunkerRegistry` will eventually enforce these namespaces in future releases.

## Best Practices

1. **Avoid Overlapping**: Do not use the `core:` namespace in plugins.
2. **Be Descriptive**: Use clear keys (e.g., `word_count` instead of `wc`).
3. **Use Primitive Types**: Metadata should be JSON-serializable (strings, numbers, booleans, lists, or nested dicts).
