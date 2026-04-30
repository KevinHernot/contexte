"""Input discovery and probing."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, Field

from contexte.constants import SUPPORTED_EXTENSIONS
from contexte.core.errors import ConfigError


class ProbeResult(BaseModel):
    path: str
    exists: bool
    is_file: bool
    file_count: int
    supported_file_count: int
    unsupported_file_count: int
    total_size_bytes: int
    file_types: dict[str, int] = Field(default_factory=dict)
    supported_files: list[str] = Field(default_factory=list)
    unsupported_files: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def discover_files(
    input_path: Path,
    *,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[Path]:
    if not input_path.exists():
        raise ConfigError(f"Input path does not exist: {input_path}")
    if input_path.is_file():
        candidates = [input_path]
        root = input_path.parent
    else:
        root = input_path
        candidates = [path for path in input_path.rglob("*") if path.is_file()]
    include_patterns = list(include or [])
    exclude_patterns = list(exclude or [])
    files = []
    for path in sorted(candidates):
        relative = _relative(path, root)
        if include_patterns and not any(relative.match(pattern) for pattern in include_patterns):
            continue
        if exclude_patterns and any(relative.match(pattern) for pattern in exclude_patterns):
            continue
        files.append(path)
    return files


def probe_path(
    input_path: Path,
    *,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    supported_extensions: set[str] | None = None,
) -> ProbeResult:
    supported_extensions = supported_extensions or SUPPORTED_EXTENSIONS
    if not input_path.exists():
        return ProbeResult(
            path=str(input_path),
            exists=False,
            is_file=False,
            file_count=0,
            supported_file_count=0,
            unsupported_file_count=0,
            total_size_bytes=0,
            warnings=["path_does_not_exist"],
        )
    files = discover_files(input_path, include=include, exclude=exclude)
    type_counts = Counter(path.suffix.lower() or "<none>" for path in files)
    supported_files = [str(path) for path in files if path.suffix.lower() in supported_extensions]
    unsupported_files = [
        str(path) for path in files if path.suffix.lower() not in supported_extensions
    ]
    warnings = []
    if unsupported_files:
        warnings.append("unsupported_files_detected")
    return ProbeResult(
        path=str(input_path),
        exists=True,
        is_file=input_path.is_file(),
        file_count=len(files),
        supported_file_count=len(supported_files),
        unsupported_file_count=len(unsupported_files),
        total_size_bytes=sum(path.stat().st_size for path in files),
        file_types=dict(sorted(type_counts.items())),
        supported_files=supported_files,
        unsupported_files=unsupported_files,
        warnings=warnings,
    )


def _relative(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)
