#!/bin/bash

# Script to generate a comprehensive prompt file containing the Contexte codebase.
# Useful for providing architecture, spec, CLI, and implementation context to LLMs.

set -euo pipefail

OUTPUT_FILE="contexte_codebase_prompt.txt"
REPO_NAME="Contexte"
MAX_LINES=5000

BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Starting ${REPO_NAME} Codebase Scan...${NC}"

cat << EOF > "$OUTPUT_FILE"
# CONTEXTE CODEBASE REVIEW PROMPT

# INSTRUCTIONS FOR LLM:
# 1. Review the entire Contexte architecture.
# 2. Focus on Context IR, .ctxpack, CLI flows, chunking, provenance, evaluation, and security.
# 3. Pay close attention to the product spec, docs, tests, and source code together.
# 4. Treat MCP as optional/experimental infrastructure, not the trusted core.
# 5. Identify consistency gaps between the spec, docs, CLI, and implementation.

EOF

add_file_to_prompt() {
    local file_path=$1
    local line_count
    local language

    line_count=$(wc -l < "$file_path")
    language=$(basename "$file_path")

    echo "Processing: $file_path (${line_count} lines)"
    echo -e "\n---" >> "$OUTPUT_FILE"
    echo "Full Path: $file_path" >> "$OUTPUT_FILE"

    if [ "$line_count" -gt "$MAX_LINES" ]; then
        echo "File Content: [SKIPPED - ${line_count} lines exceeds ${MAX_LINES} line limit]" >> "$OUTPUT_FILE"
        return
    fi

    echo "File Content:" >> "$OUTPUT_FILE"
    printf '```%s\n' "$language" >> "$OUTPUT_FILE"

    sed -E \
        -e '/^[[:space:]]*$/d' \
        -e '/^[[:space:]]*#[[:space:]]*$/d' \
        -e '/^[[:space:]]*\/\//d' \
        -e '/^[[:space:]]*\/\*/d' \
        -e '/^[[:space:]]*\*/d' \
        "$file_path" >> "$OUTPUT_FILE"

    echo '```' >> "$OUTPUT_FILE"
}

find . \
    \( \
        -type d \( \
            -name ".git" \
            -o -name ".mypy_cache" \
            -o -name ".pytest_cache" \
            -o -name ".ruff_cache" \
            -o -name ".venv" \
            -o -name "venv" \
            -o -name "dist" \
            -o -name "build" \
            -o -name "htmlcov" \
            -o -name "__pycache__" \
        \) -prune \
    \) \
    -o -type f \( \
        -name "*.py" \
        -o -name "*.md" \
        -o -name "*.toml" \
        -o -name "*.yaml" \
        -o -name "*.yml" \
        -o -name "*.json" \
        -o -name "*.sh" \
        -o -name ".gitignore" \
    \) \
    -not -name "$OUTPUT_FILE" \
    -not -path "./tests/fixtures/docs/*" \
    -print | sort | while read -r file; do
        add_file_to_prompt "$file"
    done

echo -e "${BLUE}✅ Codebase prompt generated: $OUTPUT_FILE${NC}"
