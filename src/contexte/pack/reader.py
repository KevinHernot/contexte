"""`.ctxpack` reader and validator."""

from __future__ import annotations

import hashlib
import json
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from contexte.constants import CTXPACK_SCHEMA_VERSION, MAX_DECOMPRESSED_SIZE
from contexte.core.errors import PackError
from contexte.ir.models import BuildReport, ContextChunk, ContextDocument, SecurityFinding
from contexte.ir.validate import validate_chunk, validate_document, validate_manifest
from contexte.pack.layout import (
    BUILD_REPORT_JSON,
    CHECKSUMS_JSON,
    CHUNKS_JSONL,
    DOCUMENTS_JSONL,
    MANIFEST,
    REQUIRED_FILES,
    SECURITY_FINDINGS_JSONL,
    SIGNATURE_JSON,
)
from contexte.pack.manifest import PackManifest


@dataclass(frozen=True)
class PackValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


class PackReader:
    def __init__(
        self,
        path: Path,
        *,
        skip_checksums: bool = False,
        public_key_path: Path | None = None,
    ) -> None:
        self.path = path
        self.skip_checksums = skip_checksums
        self.public_key_path = public_key_path

    def manifest(self) -> PackManifest:
        with self._zip() as archive:
            return PackManifest.model_validate_json(_read_text(archive, MANIFEST))

    def build_report(self) -> BuildReport:
        with self._zip() as archive:
            return BuildReport.model_validate_json(_read_text(archive, BUILD_REPORT_JSON))

    def iter_documents(self) -> Iterable[ContextDocument]:
        with self._zip() as archive:
            for value in _iter_jsonl(archive, DOCUMENTS_JSONL):
                yield ContextDocument.model_validate(value)

    def iter_chunks(self) -> Iterable[ContextChunk]:
        with self._zip() as archive:
            for value in _iter_jsonl(archive, CHUNKS_JSONL):
                yield ContextChunk.model_validate(value)

    def iter_findings(self) -> Iterable[SecurityFinding]:
        with self._zip() as archive:
            if SECURITY_FINDINGS_JSONL not in archive.namelist():
                return
            for value in _iter_jsonl(archive, SECURITY_FINDINGS_JSONL):
                yield SecurityFinding.model_validate(value)

    def validate(self) -> PackValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        if not self.path.exists():
            return PackValidationResult(False, [f"Pack does not exist: {self.path}"], [])
        try:
            with self._zip() as archive:
                names = set(archive.namelist())
                missing = sorted(REQUIRED_FILES - names)
                errors.extend(f"Missing required file: {name}" for name in missing)
                if MANIFEST not in names:
                    return PackValidationResult(False, errors, warnings)
                manifest = PackManifest.model_validate_json(_read_text(archive, MANIFEST))
                errors.extend(validate_manifest(manifest))
                if manifest.schema_version != CTXPACK_SCHEMA_VERSION:
                    errors.append(
                        f"Unsupported schema version {manifest.schema_version}; expected {CTXPACK_SCHEMA_VERSION}"
                    )
                if not self.skip_checksums:
                    errors.extend(_validate_checksums(archive, manifest.checksums))
                
                if SIGNATURE_JSON in names:
                    sig_data = json.loads(_read_text(archive, SIGNATURE_JSON))
                    if self.public_key_path:
                        from contexte.core.signing import verify_signature
                        if not verify_signature(archive.read(MANIFEST), sig_data["signature"], self.public_key_path):
                            errors.append("Cryptographic signature verification failed")
                elif self.public_key_path:
                    errors.append("Public key provided but pack is not signed")

                if BUILD_REPORT_JSON in names:
                    report = BuildReport.model_validate_json(_read_text(archive, BUILD_REPORT_JSON))
                    warnings.extend(report.warnings)
                doc_ids: set[str] = set()
                doc_count = 0
                for value in _iter_jsonl(archive, DOCUMENTS_JSONL):
                    doc = ContextDocument.model_validate(value)
                    doc_ids.add(doc.id)
                    doc_count += 1
                    errors.extend(validate_document(doc))
                
                chunk_count = 0
                for value in _iter_jsonl(archive, CHUNKS_JSONL):
                    chunk = ContextChunk.model_validate(value)
                    chunk_count += 1
                    errors.extend(validate_chunk(chunk))
                    if chunk.document_id not in doc_ids:
                        errors.append(f"Chunk {chunk.id} references missing document {chunk.document_id}")

                if manifest.source_summary.document_count != doc_count:
                    errors.append(f"Manifest document count mismatch: {manifest.source_summary.document_count} != {doc_count}")
                if manifest.source_summary.chunk_count != chunk_count:
                    errors.append(f"Manifest chunk count mismatch: {manifest.source_summary.chunk_count} != {chunk_count}")

                json.loads(_read_text(archive, CHECKSUMS_JSON))
        except (zipfile.BadZipFile, OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
        return PackValidationResult(valid=not errors, errors=errors, warnings=warnings)

    def read_member_text(self, name: str) -> str:
        with self._zip() as archive:
            return _read_text(archive, name)

    def _zip(self) -> zipfile.ZipFile:
        if not self.path.exists():
            raise PackError(f"Pack does not exist: {self.path}")
        archive = zipfile.ZipFile(self.path, "r")
        total_size = 0
        for info in archive.infolist():
            if info.filename.startswith("/") or ".." in info.filename:
                archive.close()
                raise PackError(f"Malicious pack detected: unsafe filename '{info.filename}'")
            total_size += info.file_size
        if total_size > MAX_DECOMPRESSED_SIZE:
            archive.close()
            raise PackError(
                f"Pack exceeds maximum allowed size ({total_size} > {MAX_DECOMPRESSED_SIZE})"
            )
        return archive


def _read_text(archive: zipfile.ZipFile, name: str) -> str:
    try:
        with archive.open(name, "r") as handle:
            return handle.read().decode("utf-8")
    except KeyError as exc:
        raise PackError(f"Pack is missing {name}") from exc


def _iter_jsonl(archive: zipfile.ZipFile, name: str) -> Iterable[dict[str, Any]]:
    text = _read_text(archive, name)
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL in {name}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL value in {name}:{line_number} must be an object")
        yield value


def _validate_checksums(archive: zipfile.ZipFile, checksums: dict[str, str]) -> list[str]:
    errors: list[str] = []
    names = set(archive.namelist())
    for name, expected in sorted(checksums.items()):
        if name not in names:
            errors.append(f"Checksum target missing: {name}")
            continue
        algorithm, _, digest = expected.partition(":")
        if algorithm != "sha256" or not digest:
            errors.append(f"Unsupported checksum format for {name}: {expected}")
            continue
        actual = hashlib.sha256(archive.read(name)).hexdigest()
        if actual != digest:
            errors.append(f"Checksum mismatch for {name}")
    return errors
