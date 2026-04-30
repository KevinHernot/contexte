"""Structured exceptions used by Contexte."""

from __future__ import annotations


class ContexteError(Exception):
    """Base class for expected Contexte failures."""


class ConfigError(ContexteError):
    """Raised for invalid pipeline configuration."""


class DecodeError(ContexteError):
    """Raised when a decoder cannot decode a source."""


class PackError(ContexteError):
    """Raised for pack read/write/validation errors."""


class ValidationError(ContexteError):
    """Raised when a pack or model is invalid."""
