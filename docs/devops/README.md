<!--
Explainer: DevOps Operating Guide for Plasma Engine Org

This document centralizes standards, workflows, and runbooks for CI/CD, Infra-as-Code, quality gates, and operational hygiene across all services in this monorepo.

Editing guidance:
- Keep sections concise and actionable. Link to deeper docs when available.
- Prefer checklists and command blocks over prose.
- Surface risks and compliance constraints inline with TODOs that include owner and context.
-->

## DevOps Operating Guide

### Scope
This guide applies to all services under `plasma-engine-org`. It complements per-repo READMEs and ADRs in `docs/adrs/`.

### Activity Log
- Canonical daily notes live in `docs/devops/activity-log.md`.
- Each entry should capture: what changed, why, outputs (redacted), decisions, blockers, and next steps.

### CI/CD Conventions (Draft)
- CI pipeline templates live in `ci/` (not active by default). To activate for GitHub, copy into `.github/workflows/`.
- Required stages: lint, test, build, package, publish (as applicable per language).
- Artifacts and cache keys must be deterministic and include lockfile hashes.

### Infrastructure-as-Code (Draft)
- Root IaC starter is in `infra/terraform/` with provider pinning and module layout.
- Environments are separated by directory (e.g., `envs/dev`, `envs/stage`, `envs/prod`) with shared modules.
- Remote state and secrets must be configured before any `apply`.

### Quality Gates
- Python: `ruff` for lint, `black` for format. JS/TS: `eslint`, `prettier`.
- Run `scripts/lint-all.sh` and `scripts/format-all.sh` locally and in CI.

### Research Index
- Exa API schemas mirrored to `docs/exa/` as JSON/YAML plus Markdown summaries for downstream agents.

### TODOs
- [ ] TODO(ops@plasma): Finalize CI template matrix for Python and Node projects.
- [ ] TODO(infra@plasma): Choose remote state backend (S3/Dynamo or GCS/Lock) and wire provider auth.
- [ ] TODO(security@plasma): Define secrets management approach (Vault/SM) and rotate bootstrap tokens.

