"""Default build pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from contexte.chunkers.base import ChunkerConfig
from contexte.chunkers.fixed import FixedChunker
from contexte.chunkers.heading import HeadingChunker
from contexte.chunkers.semantic_placeholder import SemanticChunkerPlaceholder
from contexte.core.config import PipelineConfig, load_config, merge_cli_overrides
from contexte.core.discovery import ProbeResult, discover_files, probe_path
from contexte.core.errors import ConfigError, PackError
from contexte.core.hashing import sha256_file, stable_json_hash
from contexte.core.ids import document_id
from contexte.decoders.base import DecodeContext
from contexte.decoders.registry import default_registry
from contexte.ir.models import (
    BuildReport,
    ChunkingStats,
    ContextChunk,
    ContextDocument,
    SecurityFinding,
)
from contexte.normalizers.dedupe import annotate_duplicate_chunks
from contexte.normalizers.metadata import source_ref_for_path
from contexte.pack.manifest import PackManifest
from contexte.pack.reader import PackReader
from contexte.pack.writer import write_pack
from contexte.security.scanners import scan_chunk_security, scan_document_security


@dataclass
class BuildResult:
    output: Path
    manifest: PackManifest
    build_report: BuildReport
    documents: list[ContextDocument]
    chunks: list[ContextChunk]
    findings: list[SecurityFinding]


def probe(input_path: Path, *, config_path: Path | None = None) -> ProbeResult:
    config = load_config(config_path)
    registry = default_registry()

    def explainer(path: Path) -> str:
        from contexte.ir.models import SourceRef

        ref = SourceRef(uri=str(path), type="file", original_path=str(path))
        return registry.explain_support(ref)

    return probe_path(
        input_path,
        include=config.input.include,
        exclude=config.input.exclude,
        supported_extensions=registry.supported_extensions(),
        explainer=explainer,
    )


def build_context_pack(
    input_path: Path,
    output_path: Path,
    *,
    config_path: Path | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    chunker: str | None = None,
    max_chars: int = 3000,
    force: bool = False,
    private_key_path: Path | None = None,
) -> BuildResult:
    base_config = load_config(config_path)
    config = merge_cli_overrides(
        base_config,
        include=include,
        exclude=exclude,
        chunker=chunker,
        max_chars=max_chars,
        output_pack=output_path,
    )
    if config.chunking.max_chars <= 0:
        raise ConfigError("chunking.max_chars must be greater than zero")
    if config.chunking.overlap_chars < 0:
        raise ConfigError("chunking.overlap_chars must not be negative")

    input_path = input_path.resolve()
    source_root = input_path if input_path.is_dir() else input_path.parent
    registry = default_registry()
    files = discover_files(input_path, include=config.input.include, exclude=config.input.exclude)
    config_payload = config.model_dump(mode="json")
    config_hash = stable_json_hash(config_payload)
    deterministic_ts = os.environ.get("CONTEXTE_DETERMINISTIC_TIMESTAMP")
    if deterministic_ts:
        extracted_at = datetime.fromisoformat(deterministic_ts)
        if extracted_at.tzinfo is None:
            extracted_at = extracted_at.replace(tzinfo=UTC)
    else:
        extracted_at = datetime.now(UTC)

    documents: list[ContextDocument] = []
    chunks: list[ContextChunk] = []
    findings: list[SecurityFinding] = []
    warnings: list[str] = []
    errors: list[str] = []
    unsupported_count = 0
    failed_count = 0
    empty_document_count = 0
    seen_hashes: dict[str, Path] = {}

    chunker_impl = _chunker_from_config(config)

    for path in files:
        try:
            source_hash = sha256_file(path)
            source_ref = source_ref_for_path(path, sha256=source_hash, root=source_root)
        except OSError as exc:
            failed_count += 1
            errors.append(f"{path}: cannot read file ({exc})")
            continue
        if source_hash in seen_hashes:
            warnings.append(f"exact_duplicate_source:{path}:{seen_hashes[source_hash]}")
        else:
            seen_hashes[source_hash] = path
        decoder = registry.decoder_for(source_ref)
        if decoder is None:
            unsupported_count += 1
            warnings.append(f"unsupported_file:{path}")
            continue
        doc_id = document_id(source_hash, source_ref.original_path or source_ref.uri)
        context = DecodeContext(
            source_root=source_root,
            document_id=doc_id,
            source_ref=source_ref,
            pipeline_config_hash=config_hash,
            extracted_at=extracted_at,
        )
        try:
            document = decoder.decode(path, context)
        except Exception as exc:
            failed_count += 1
            errors.append(f"{path}: decoder {getattr(decoder, 'id', 'unknown')} failed ({exc})")
            continue
        if document.errors:
            for error in document.errors:
                message = f"{path}:{error.code}:{error.message}"
                if error.severity in {"error", "critical"}:
                    errors.append(message)
                else:
                    warnings.append(message)
        if not document.blocks:
            empty_document_count += 1
            failed_count += 1
            warnings.append(f"empty_document:{path}")
            continue
        findings.extend(
            scan_document_security(
                document,
                pii=config.security.pii,
                secrets=config.security.secrets,
                prompt_injection=config.security.prompt_injection,
            )
        )
        document_chunks = chunker_impl.chunk(document)
        if not document_chunks:
            warnings.append(f"no_chunks:{path}")
        for chunk in document_chunks:
            findings.extend(
                scan_chunk_security(
                    chunk,
                    pii=config.security.pii,
                    secrets=config.security.secrets,
                    prompt_injection=config.security.prompt_injection,
                )
            )
        documents.append(document)
        chunks.extend(document_chunks)

    duplicate_chunk_ratio = annotate_duplicate_chunks(chunks)
    if duplicate_chunk_ratio:
        warnings.append(f"duplicate_chunk_ratio:{duplicate_chunk_ratio:.3f}")

    chunk_lengths = [len(c.text) for c in chunks]
    chunking_stats = None
    if chunk_lengths:
        chunking_stats = ChunkingStats(
            min_chars=min(chunk_lengths),
            max_chars=max(chunk_lengths),
            avg_chars=sum(chunk_lengths) / len(chunk_lengths),
            median_chars=sorted(chunk_lengths)[len(chunk_lengths) // 2],
            total_chars=sum(chunk_lengths),
        )

    build_report = BuildReport(
        source_root=str(input_path),
        discovered_file_count=len(files),
        supported_file_count=len(files) - unsupported_count,
        unsupported_file_count=unsupported_count,
        failed_file_count=failed_count,
        document_count=len(documents),
        chunk_count=len(chunks),
        chunking_stats=chunking_stats,
        security_finding_count=len(findings),
        warnings=warnings,
        errors=errors,
        created_at=datetime.now(tz=UTC),
        empty_document_count=empty_document_count,
    )
    manifest = write_pack(
        output_path,
        source_root=str(input_path),
        documents=documents,
        chunks=chunks,
        findings=findings,
        build_report=build_report,
        pipeline_config=config_payload,
        force=force,
        private_key_path=private_key_path,
    )

    validation = PackReader(output_path).validate()
    if not validation.valid:
        raise PackError(f"Post-build validation failed:\n" + "\n".join(validation.errors))

    return BuildResult(
        output=output_path,
        manifest=manifest,
        build_report=build_report,
        documents=documents,
        chunks=chunks,
        findings=findings,
    )


def _chunker_from_config(config: PipelineConfig) -> Any:
    chunker_config = ChunkerConfig(
        max_chars=config.chunking.max_chars,
        overlap_chars=config.chunking.overlap_chars,
    )
    if config.chunking.strategy == "fixed":
        return FixedChunker(chunker_config)
    if config.chunking.strategy == "heading":
        return HeadingChunker(chunker_config)
    return SemanticChunkerPlaceholder()
