"""Plugin discovery via Python entry points."""

from __future__ import annotations

from importlib.metadata import entry_points

from contexte.plugins.api import ContextePlugin, PluginRegistry

ENTRY_POINT_GROUP = "contexte.plugins"


def load_plugins() -> PluginRegistry:
    registry = PluginRegistry()
    discovered = entry_points()
    selected = discovered.select(group=ENTRY_POINT_GROUP) if hasattr(discovered, "select") else []
    for entry_point in selected:
        plugin_cls = entry_point.load()
        plugin: ContextePlugin = plugin_cls()
        plugin.register(registry)
    return registry
