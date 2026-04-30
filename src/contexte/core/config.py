"""Pipeline configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from contexte.constants import DEFAULT_EXCLUDES, DEFAULT_MAX_CHARS, DEFAULT_OVERLAP_CHARS
from contexte.core.errors import ConfigError


class InputConfig(BaseModel):
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=lambda: sorted(DEFAULT_EXCLUDES))


class ChunkingConfig(BaseModel):
    strategy: Literal["heading", "fixed", "semantic"] = "heading"
    max_chars: int = DEFAULT_MAX_CHARS
    overlap_chars: int = DEFAULT_OVERLAP_CHARS


class SecurityConfig(BaseModel):
    pii: bool = True
    secrets: bool = True
    prompt_injection: bool = True


class ReportConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    html: bool = True
    json_enabled: bool = Field(default=True, validation_alias="json", serialization_alias="json")


class OutputConfig(BaseModel):
    pack: str | None = None
    report: str | None = None


class PipelineConfig(BaseModel):
    schema_version: str = "0.1"
    input: InputConfig = Field(default_factory=InputConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    report: ReportConfig = Field(default_factory=ReportConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)


def load_config(path: Path | None) -> PipelineConfig:
    if path is None:
        return PipelineConfig()
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    data: dict[str, Any]
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        try:
            import yaml
        except Exception as exc:  # pragma: no cover - dependency resolution
            raise ConfigError("YAML config requires PyYAML to be installed") from exc
        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ConfigError("Config file must contain a mapping at the top level")
        data = loaded
    return PipelineConfig.model_validate(data)


def merge_cli_overrides(
    config: PipelineConfig,
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    chunker: str | None = None,
    max_chars: int | None = None,
    output_pack: Path | None = None,
) -> PipelineConfig:
    data = config.model_dump(mode="json")
    if include:
        data["input"]["include"] = include
    if exclude:
        data["input"]["exclude"] = [*data["input"].get("exclude", []), *exclude]
    if chunker:
        data["chunking"]["strategy"] = chunker
    if max_chars is not None:
        data["chunking"]["max_chars"] = max_chars
    if output_pack is not None:
        data["output"]["pack"] = str(output_pack)
    return PipelineConfig.model_validate(data)
