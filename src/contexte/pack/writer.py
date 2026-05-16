"""Atomic `.ctxpack` writer."""

from __future__ import annotations

import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from contexte.core.errors import PackError
from contexte.core.hashing import checksum_for_file, stable_json_hash
from contexte.core.ids import pack_id
from contexte.ir.models import BuildReport, ContextChunk, ContextDocument, SecurityFinding
from contexte.ir.serialize import dumps_json, write_json, write_jsonl
from contexte.ir.validate import validate_chunk, validate_document
from contexte.pack.layout import (
    BUILD_REPORT_JSON,
    CHECKSUMS_JSON,
    CHUNKS_JSONL,
    DOCUMENTS_JSONL,
    MANIFEST,
    NORMALIZED_MARKDOWN_DIR,
    PIPELINE_JSON,
    SECURITY_FINDINGS_JSONL,
    SIGNATURE_JSON,
    SOURCES_JSONL,
)
from contexte.pack.manifest import PackFeatures, PackManifest, SourceSummary

_FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def write_pack(
    output: Path,
    *,
    source_root: str,
    documents: list[ContextDocument],
    chunks: list[ContextChunk],
    findings: list[SecurityFinding],
    build_report: BuildReport,
    pipeline_config: dict[str, Any],
    force: bool = False,
    include_normalized_markdown: bool = True,
    private_key_path: Path | None = None,
) -> PackManifest:
    output = output.resolve()
    if output.exists() and not force:
        raise PackError(f"Output already exists: {output}. Use --force to overwrite.")
    if output.suffix != ".ctxpack":
        raise PackError("Output path must end with .ctxpack")

    validation_errors = []
    for document in documents:
        validation_errors.extend(validate_document(document))
    for chunk in chunks:
        validation_errors.extend(validate_chunk(chunk))
    if validation_errors:
        joined = "\n".join(validation_errors)
        raise PackError(f"Refusing to write invalid pack:\n{joined}")

    temp_dir = output.with_suffix(output.suffix + ".tmp")
    temp_zip = output.with_suffix(output.suffix + ".partial")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    if temp_zip.exists():
        temp_zip.unlink()
    temp_dir.mkdir(parents=True)

    try:
        write_jsonl(temp_dir / DOCUMENTS_JSONL, documents)
        write_jsonl(temp_dir / CHUNKS_JSONL, chunks)
        write_json(temp_dir / BUILD_REPORT_JSON, build_report, pretty=True)
        write_jsonl(temp_dir / SECURITY_FINDINGS_JSONL, findings)
        write_jsonl(temp_dir / SOURCES_JSONL, [document.source for document in documents])
        write_json(temp_dir / PIPELINE_JSON, pipeline_config, pretty=True)
        if include_normalized_markdown:
            _write_normalized_markdown(temp_dir, documents)

        checksums = _checksums(temp_dir, exclude={MANIFEST, CHECKSUMS_JSON})
        write_json(temp_dir / CHECKSUMS_JSON, checksums, pretty=True)

        manifest = PackManifest(
            pack_id=pack_id(
                stable_json_hash({"source_root": source_root, "docs": [d.id for d in documents]})
            ),
            created_at=datetime.now(tz=UTC),
            source_summary=SourceSummary(
                source_root=source_root,
                document_count=len(documents),
                chunk_count=len(chunks),
            ),
            features=PackFeatures(
                has_documents=True,
                has_chunks=True,
                has_security_findings=bool(findings),
                has_eval=False,
                has_embeddings=False,
            ),
            checksums=checksums,
            metadata={"build_report": BUILD_REPORT_JSON},
        )
        manifest_bytes = write_json(temp_dir / MANIFEST, manifest, pretty=True)

        if private_key_path:
            from contexte.core.signing import sign_data
            signature = sign_data(manifest_bytes, private_key_path)
            write_json(temp_dir / SIGNATURE_JSON, {"signature": signature, "algorithm": "ed25519"})

        _zip_dir(temp_dir, temp_zip)
        if output.exists():
            output.unlink()
        temp_zip.replace(output)
        return manifest
    finally:
        if temp_zip.exists():
            temp_zip.unlink()
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def _checksums(root: Path, *, exclude: set[str]) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in exclude:
            continue
        checksums[relative] = checksum_for_file(path)
    return checksums


def _zip_dir(root: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=_FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())


def _write_normalized_markdown(root: Path, documents: list[ContextDocument]) -> None:
    markdown_root = root / NORMALIZED_MARKDOWN_DIR
    markdown_root.mkdir(parents=True, exist_ok=True)
    for document in documents:
        body_parts = []
        for block in document.blocks:
            text = block.markdown or block.text or ""
            if not text.strip():
                continue
            if block.type == "heading":
                level = min(6, max(1, block.level or 1))
                body_parts.append(f"{'#' * level} {block.text or text}")
            else:
                body_parts.append(text)
        frontmatter = {
            "document_id": document.id,
            "source_uri": document.source.uri,
            "title": document.title or document.id,
        }
        content = "---\n" + dumps_json(frontmatter, pretty=True).strip() + "\n---\n\n"
        content += "\n\n".join(body_parts).strip() + "\n"
        (markdown_root / f"{document.id}.md").write_text(content, encoding="utf-8")
