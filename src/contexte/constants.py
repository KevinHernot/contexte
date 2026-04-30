"""Project-wide constants."""

from __future__ import annotations

CONTEXT_IR_SCHEMA_VERSION = "0.1.0"
CTXPACK_SCHEMA_VERSION = "0.1.0"
CONTEXT_VERSION = "0.1.0"
CREATED_BY = "contexte"
DEFAULT_MAX_CHARS = 3000
DEFAULT_OVERLAP_CHARS = 200
SUPPORTED_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".pdf", ".docx", ".csv", ".json"}
DEFAULT_EXCLUDES = {
    "**/.git/**",
    "**/.hg/**",
    "**/.svn/**",
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/dist/**",
    "**/build/**",
    "**/.venv/**",
    "**/venv/**",
}
