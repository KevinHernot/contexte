"""LangChain document exporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from contexte.pack.reader import PackReader
from contexte.security.redaction import redact_document


class LangChainExporter:
    """Exports context pack documents as LangChain Document objects."""

    id: str = "langchain"

    def __init__(self, *, redact: bool = False) -> None:
        self.redact = redact

    def export(self, reader: PackReader, output: Path) -> None:
        """
        Exports all documents in the pack as a JSON file containing serialized LangChain Documents.
        
        Note: This does not require langchain-core at runtime for JSON export, 
        but follows the LangChain schema.
        """
        lc_docs: list[dict[str, Any]] = []
        
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
            
            # Map to LangChain schema
            lc_doc = {
                "page_content": full_text,
                "metadata": {
                    "source": doc.source.uri,
                    "title": doc.title or doc.id,
                    "document_id": doc.id,
                    "contexte_id": doc.id,
                    "pack_id": reader.manifest().pack_id,
                    **doc.metadata,
                }
            }
            lc_docs.append(lc_doc)

        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as f:
            json.dump(lc_docs, f, ensure_ascii=False, indent=2)
