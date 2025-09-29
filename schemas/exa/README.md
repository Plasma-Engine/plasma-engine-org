# Local Mirror of Exa API Schemas

This folder contains local JSON/YAML mirrors of Exa API schemas for offline development.

- Source of truth: Exa documentation (`https://docs.exa.ai/`).
- Update process: Run `scripts/mirror-exa-schemas.py` to refresh placeholders or pull authoritative schemas via Rube MCP.
- Validation: Use these schemas for contract tests and input validation.