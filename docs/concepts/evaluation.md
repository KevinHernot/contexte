# Evaluation

The basic v0.1 eval suite measures pack quality and safety.

Metrics include:

- document count;
- chunk count;
- unsupported and failed files;
- empty document/chunk counts;
- average, median, and max chunk length;
- chunks without source refs;
- citation coverage;
- duplicate chunk ratio;
- PII, secret, and prompt-injection finding counts;
- warnings.

## RAG readiness score

The score starts at 100 and subtracts heuristic penalties for failed files, empty documents, missing citations, duplicates, security findings, unsupported files, and poor average chunk length.

It is a practical triage signal, not a scientific benchmark and not a guarantee of RAG performance.
