"""Exporter protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from contexte.pack.reader import PackReader


class Exporter(Protocol):
    id: str

    def export(self, reader: PackReader, output: Path) -> None: ...
