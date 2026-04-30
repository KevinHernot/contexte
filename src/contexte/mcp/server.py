"""Optional read-only serving adapter placeholders."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from contexte.core.errors import ConfigError


def serve_adapter_placeholder(
    path: Path,
    *,
    mode: Literal["mcp", "http"],
    port: int = 8787,
    read_only: bool = True,
) -> None:
    if not read_only:
        raise ConfigError(
            "Contexte v0.1 does not support write-enabled serving. Future adapters default to --read-only."
        )
    adapter = "MCP" if mode == "mcp" else "HTTP"
    raise ConfigError(
        f"{adapter} serving for {path} on port {port} is not part of the v0.1 trust core. "
        "Future adapters are planned as optional read-only exports; for now use ctx export or the lexical helpers in contexte.mcp.tools."
    )


def serve_mcp(path: Path, *, port: int = 8787) -> None:
    serve_adapter_placeholder(path, mode="mcp", port=port, read_only=True)
