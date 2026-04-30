# RFC 0003: Plugin API

## Status

Draft for v0.1, target stabilization in v0.2.

## Summary

Plugins register optional decoders, chunkers, exporters, and eval suites through Python entry points.

## Decision

Use entry point group `contexte.plugins` and a small `PluginRegistry` in `contexte.plugins.api`.
