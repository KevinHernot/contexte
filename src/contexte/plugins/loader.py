"""Plugin discovery via Python entry points."""

from __future__ import annotations

from importlib.metadata import entry_points

from contexte.plugins.api import ContextePlugin, PluginRegistry

ENTRY_POINT_GROUP = "contexte.plugins"


_REGISTRY: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = load_plugins()
    return _REGISTRY


def load_plugins() -> PluginRegistry:
    registry = PluginRegistry()
    discovered = entry_points()
    selected = (
        discovered.select(group=ENTRY_POINT_GROUP) if hasattr(discovered, "select") else []
    )
    for entry_point in selected:
        try:
            plugin_cls = entry_point.load()
            plugin: ContextePlugin = plugin_cls()
            plugin.register(registry)
        except Exception:
            # Skip broken plugins
            continue
    return registry
