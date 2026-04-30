"""File metadata normalization."""

from __future__ import annotations

import mimetypes
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from contexte.ir.models import SourceRef


def datetime_from_timestamp(timestamp: float | None) -> datetime | None:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=UTC)


def source_ref_for_path(path: Path, *, sha256: str, root: Path | None = None) -> SourceRef:
    resolved = path.resolve()
    media_type, _ = mimetypes.guess_type(str(path))
    try:
        original_path = str(resolved.relative_to(root.resolve())) if root else str(path)
    except ValueError:
        original_path = str(path)
    stat = path.stat()
    return SourceRef(
        uri=resolved.as_uri(),
        type="file",
        media_type=media_type,
        size_bytes=stat.st_size,
        sha256=sha256,
        original_path=original_path,
    )


def file_times(path: Path) -> dict[str, datetime | None]:
    stat = path.stat()
    created_timestamp = getattr(stat, "st_birthtime", None)
    return {
        "created_at": datetime_from_timestamp(created_timestamp),
        "modified_at": datetime_from_timestamp(stat.st_mtime),
    }


def file_metadata(path: Path, *, root: Path | None = None) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        relative_path = str(resolved.relative_to(root.resolve())) if root else path.name
    except ValueError:
        relative_path = path.name
    stat = path.stat()
    modified_at = datetime_from_timestamp(stat.st_mtime)
    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "relative_path": relative_path,
        "size_bytes": stat.st_size,
        "modified_at": modified_at.isoformat() if modified_at else None,
    }
