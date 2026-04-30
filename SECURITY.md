# Security Policy

## Supported versions

Contexte is pre-1.0. Security fixes target the latest released version unless otherwise documented.

## Reporting vulnerabilities

Please do not open public issues for vulnerabilities. Report security concerns privately to the maintainers with:

- affected version or commit;
- reproduction steps;
- impact assessment;
- any suggested mitigation.

## Security scope

Contexte processes local documents and context packs. In scope:

- unsafe archive handling;
- path traversal;
- secret or PII handling bugs;
- pack validation bypasses;
- unexpected network access from core code.

## Sensitive data policy

Core Contexte never uploads user data by default. Future plugins that call external services must require explicit opt-in and clear documentation.
