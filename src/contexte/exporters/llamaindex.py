"""LlamaIndex document exporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from contexte.pack.reader import PackReader
from contexte.security.redaction import redact_document


class LlamaIndexExporter:
    """Exports context pack documents as LlamaIndex Document objects."""

    id: str = "llamaindex"

    def __init__(self, *, redact: bool = False) -> None:
        self.redact = redact

    def export(self, reader: PackReader, output: Path) -> None:
        """
        Exports all documents in the pack as a JSON file containing serialized LlamaIndex Documents.
        """
        li_docs: list[dict[str, Any]] = []
        
        # Load findings if redaction is requested
        findings_map: dict[str, list[Any]] = {}
        if self.redact:
            for finding in reader.iter_findings():
                findings_map.setdefault(finding.document_id, []).append(finding)

        for doc in reader.iter_documents():
            if self.redact and doc.id in findings_map:
                doc = redact_document(doc, findings_map[doc.id])
            
            # Reconstruct text from blocks
            text_parts = []
            for block in doc.blocks:
                text_parts.append(block.text or block.markdown or "")
            
            full_text = "\n\n".join(text_parts)
            
            # Map to LlamaIndex schema
            li_doc = {
                "text": full_text,
                "id_": doc.id,
                "metadata": {
                    "file_name": doc.source.uri,
                    "document_title": doc.title or doc.id,
                    "contexte_pack_id": reader.manifest().pack_id,
                    **doc.metadata,
                },
                "excluded_embed_metadata_keys": ["contexte_pack_id"],
                "excluded_llm_metadata_keys": ["contexte_pack_id"],
            }
            li_docs.append(li_doc)

        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as f:
            json.dump(li_docs, f, ensure_ascii=False, indent=2)
