# Security

Contexte marks security findings as metadata. v0.1 does not delete or redact content by default.

## Secret scanning

Regex checks cover:

- AWS access key IDs;
- private key headers;
- GitHub tokens;
- Slack tokens;
- generic API keys;
- long high-entropy tokens.

## PII scanning

Regex checks cover:

- email addresses;
- phone-like numbers;
- credit-card candidates with Luhn validation;
- IP addresses;
- US SSN candidates;
- IBAN-like values.

## Prompt injection heuristics

The scanner marks text such as:

- “ignore previous instructions”;
- “reveal hidden prompt”;
- “developer message”;
- “system prompt”;
- “tool call”;
- “exfiltrate”.

## Safe defaults

Core Contexte is local-first and performs no network calls. Future plugins that call external APIs must require explicit opt-in.
