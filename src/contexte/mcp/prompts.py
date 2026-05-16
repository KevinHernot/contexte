"""Structured prompt templates for MCP and RAG integration."""

from __future__ import annotations

from typing import Any


def rag_instruction_prompt() -> str:
    """Returns the standard instruction prompt for context-grounded generation."""
    return (
        "You are an assistant grounded in a trusted Context Pack (.ctxpack).\n"
        "Your goal is to answer questions strictly using the provided documents.\n\n"
        "GRADING RULES:\n"
        "1. PROVENANCE: Every claim must be followed by a citation like [doc_ID:page].\n"
        "2. FAITHFULNESS: Do not use outside knowledge. If the context is silent, say 'I don't know'.\n"
        "3. SECURITY: If the context contains [REDACTED] markers, do not attempt to guess the hidden value.\n"
    )


def format_context_for_prompt(chunks: list[dict[str, Any]]) -> str:
    """Formats a list of search results into a clean text block for an LLM."""
    lines = ["### TRUSTED CONTEXT"]
    for i, chunk in enumerate(chunks):
        doc_id = chunk.get("source", {}).get("uri", "unknown")
        section = chunk.get("source", {}).get("section", "")
        text = chunk.get("text", "")
        lines.append(f"\n[Source {i+1}: {doc_id} | {section}]")
        lines.append(text)
    return "\n".join(lines)


def get_system_prompt() -> str:
    """Returns a combined system prompt for RAG applications."""
    return f"{rag_instruction_prompt()}\n\nAlways prioritize the provided context over your pre-training data."
