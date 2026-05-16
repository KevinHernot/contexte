"""Basic v0.1 context quality evaluation."""

from __future__ import annotations

from pathlib import Path

from contexte.eval.metrics import average, duplicate_chunk_ratio, median_int
from contexte.ir.models import (
    BasicEvalReport,
    BuildReport,
    ContextChunk,
    ContextDocument,
    SecurityFinding,
)
from contexte.pack.reader import PackReader
from contexte.plugins.api import EvalMetric


def evaluate_pack(path: Path, reference_path: Path | None = None) -> BasicEvalReport:
    reader = PackReader(path)
    reference_reader = PackReader(reference_path) if reference_path else None
    
    from contexte.plugins.loader import get_plugin_registry

    registry = get_plugin_registry()
    
    return evaluate_values(
        documents=list(reader.iter_documents()),
        chunks=list(reader.iter_chunks()),
        findings=list(reader.iter_findings()),
        build_report=reader.build_report(),
        reference_documents=list(reference_reader.iter_documents()) if reference_reader else None,
        reference_chunks=list(reference_reader.iter_chunks()) if reference_reader else None,
        plugin_metrics=registry.metrics,
    )


def evaluate_values(
    *,
    documents: list[ContextDocument],
    chunks: list[ContextChunk],
    findings: list[SecurityFinding],
    build_report: BuildReport,
    reference_documents: list[ContextDocument] | None = None,
    reference_chunks: list[ContextChunk] | None = None,
    plugin_metrics: list[EvalMetric] | None = None,
) -> BasicEvalReport:
    lengths = [chunk.char_count for chunk in chunks]
    empty_documents = sum(
        1 for document in documents if not any(_block_text(block) for block in document.blocks)
    )
    empty_documents += build_report.empty_document_count
    empty_chunks = sum(1 for chunk in chunks if not chunk.text.strip())
    chunks_without_source_refs = sum(1 for chunk in chunks if not chunk.source_refs)
    chunks_without_citations_ratio = chunks_without_source_refs / len(chunks) if chunks else 0.0
    duplicate_ratio = duplicate_chunk_ratio(chunks)
    pii_count = sum(1 for finding in findings if finding.type == "pii")
    secret_count = sum(1 for finding in findings if finding.type == "secret")
    prompt_count = sum(1 for finding in findings if finding.type == "prompt_injection")
    warnings = [*build_report.warnings]
    for chunk in chunks:
        warnings.extend(chunk.quality.warnings)
    score, explanation = rag_readiness_score(
        document_count=len(documents),
        discovered_file_count=build_report.discovered_file_count,
        failed_file_count=build_report.failed_file_count,
        unsupported_file_count=build_report.unsupported_file_count,
        empty_document_count=empty_documents,
        chunks_without_citations_ratio=chunks_without_citations_ratio,
        duplicate_chunk_ratio=duplicate_ratio,
        pii_finding_count=pii_count,
        secret_finding_count=secret_count,
        avg_chunk_chars=average(lengths),
    )

    if reference_documents is not None:
        ref_ids = {doc.id for doc in reference_documents}
        curr_ids = {doc.id for doc in documents}
        missing = ref_ids - curr_ids
        recall = len(ref_ids - missing) / len(ref_ids) if ref_ids else 1.0
        
        if recall < 1.0:
            penalty = 30 * (1.0 - recall)
            score -= penalty
            explanation.append(f"-{penalty:.1f}: document recall {recall:.1%} (missing {len(missing)} docs from reference).")
        else:
            explanation.append("+0.0: document recall is 100% (matches reference).")

    plugin_results = {}
    if plugin_metrics:
        for metric in plugin_metrics:
            try:
                plugin_results[metric.id] = metric.compute(documents, chunks)
            except Exception as exc:
                warnings.append(f"plugin_metric_error:{metric.id}:{exc}")

    return BasicEvalReport(
        document_count=len(documents),
        chunk_count=len(chunks),
        unsupported_file_count=build_report.unsupported_file_count,
        failed_file_count=build_report.failed_file_count,
        empty_document_count=empty_documents,
        empty_chunk_count=empty_chunks,
        avg_chunk_chars=average(lengths),
        median_chunk_chars=median_int(lengths),
        max_chunk_chars=max(lengths, default=0),
        chunks_without_source_refs=chunks_without_source_refs,
        chunks_without_citations_ratio=chunks_without_citations_ratio,
        duplicate_chunk_ratio=duplicate_ratio,
        pii_finding_count=pii_count,
        secret_finding_count=secret_count,
        prompt_injection_finding_count=prompt_count,
        security_findings=findings,
        plugin_metrics=plugin_results,
        warnings=sorted(set(warnings)),
        rag_readiness_score=score,
        score_explanation=explanation,
    )


def rag_readiness_score(
    *,
    document_count: int,
    discovered_file_count: int,
    failed_file_count: int,
    unsupported_file_count: int,
    empty_document_count: int,
    chunks_without_citations_ratio: float,
    duplicate_chunk_ratio: float,
    pii_finding_count: int,
    secret_finding_count: int,
    avg_chunk_chars: float,
) -> tuple[int, list[str]]:
    score = 100.0
    explanation: list[str] = [
        "Starts at 100; penalties are heuristic triage signals and not guarantees of RAG performance."
    ]
    denominator = max(1, discovered_file_count)
    failed_ratio = failed_file_count / denominator
    unsupported_ratio = unsupported_file_count / denominator
    empty_document_ratio = empty_document_count / max(1, document_count + empty_document_count)
    if failed_ratio:
        penalty = 20 * failed_ratio
        score -= penalty
        explanation.append(f"-{penalty:.1f}: failed file ratio {failed_ratio:.1%}.")
    if empty_document_ratio:
        penalty = 15 * empty_document_ratio
        score -= penalty
        explanation.append(f"-{penalty:.1f}: empty document ratio {empty_document_ratio:.1%}.")
    if chunks_without_citations_ratio:
        penalty = 15 * chunks_without_citations_ratio
        score -= penalty
        explanation.append(
            f"-{penalty:.1f}: chunks without citations {chunks_without_citations_ratio:.1%}."
        )
    if duplicate_chunk_ratio:
        penalty = 10 * duplicate_chunk_ratio
        score -= penalty
        explanation.append(
            f"-{penalty:.1f}: exact duplicate chunk ratio {duplicate_chunk_ratio:.1%}."
        )
    if pii_finding_count:
        score -= 10
        explanation.append("-10.0: PII findings require review.")
    if secret_finding_count:
        score -= 10
        explanation.append("-10.0: secret findings require review.")
    if unsupported_ratio > 0.2:
        score -= 10
        explanation.append("-10.0: many files are unsupported.")
    if avg_chunk_chars and not 300 <= avg_chunk_chars <= 5000:
        score -= 10
        explanation.append("-10.0: average chunk length is outside the recommended range.")
    return max(0, min(100, round(score))), explanation


def _block_text(block: object) -> str:
    return str(getattr(block, "text", None) or getattr(block, "markdown", None) or "").strip()
