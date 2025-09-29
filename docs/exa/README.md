<!--
Explainer: Authoritative mirror of Exa API reference for downstream agents.
This folder contains JSON/YAML schemas and Markdown summaries for key endpoints.
Source of truth: Exa official docs. Replace placeholders once Rube MCP provides verified schemas.
-->

## Exa API Reference (Mirrored)

Contents:
- `schemas/` — JSON Schema and YAML definitions for endpoints
- `SUMMARY.md` — Human-readable summaries with request/response examples

### Update Process
1. Use Rube MCP to fetch official Exa docs and OpenAPI/spec content.
2. Update `schemas/*.json` and `schemas/*.yaml` with verified fields and enums.
3. Update `SUMMARY.md` with examples and cite the exact source URLs.

### TODOs
- [ ] TODO(research@plasma): Verify endpoints and models against official Exa docs.
- [ ] TODO(agents@plasma): Add usage examples aligned with agent capabilities.

