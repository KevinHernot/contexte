"""Public plugin API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from contexte.chunkers.base import Chunker
from contexte.decoders.base import Decoder
from contexte.exporters.base import Exporter


class EvalSuite(Protocol):
    id: str


class ContextePlugin(Protocol):
    id: str
    version: str

    def register(self, registry: PluginRegistry) -> None: ...


@dataclass
class PluginRegistry:
    decoders: list[Decoder] = field(default_factory=list)
    chunkers: list[Chunker] = field(default_factory=list)
    exporters: list[Exporter] = field(default_factory=list)
    eval_suites: list[EvalSuite] = field(default_factory=list)

    def register_decoder(self, decoder: Decoder) -> None:
        self.decoders.append(decoder)

    def register_chunker(self, chunker: Chunker) -> None:
        self.chunkers.append(chunker)

    def register_exporter(self, exporter: Exporter) -> None:
        self.exporters.append(exporter)

    def register_eval_suite(self, suite: EvalSuite) -> None:
        self.eval_suites.append(suite)
