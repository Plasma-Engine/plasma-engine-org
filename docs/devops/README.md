# DevOps Seed — Infrastructure & Automation

This folder contains the initial, highly-commented starter assets to bootstrap infrastructure-as-code, CI/CD automation, and operational scripts for the Plasma Engine program.

- Purpose: Provide extendable, well-documented baselines other agents can safely build on.
- Scope: Terraform skeleton, reusable CI workflows (templates), and environment bootstrap utilities.
- Ownership: DevOps Execution Agent (seed). Downstream owners should clone, adapt, and harden for their domains.

## Contents

- `infra/terraform/` — Cloud-agnostic Terraform skeleton with AWS defaults; switchable via variables.
- `ci/github/workflows/` — Reusable GitHub Actions workflow templates covering lint, test, scan, build, and Terraform.
- `scripts/` — Bootstrap and developer utilities (environment setup, lint orchestration, schema mirroring).
- `schemas/exa/` — Local mirrors of Exa API schemas (JSON/YAML) with field-level comments.

## Working Agreements

- Comment density: Prefer more comments than fewer. Each file includes an explainer and TODOs where follow-up decisions are required.
- Cross-links: Comments reference authoritative docs (Terraform, GitHub Actions, Exa) when relevant.
- Reuse first: Consume reusable workflows via `workflow_call` instead of duplicating YAML in each service repo.
- Tooling: Prefer the Rube MCP for external lookups; fall back to local shell when MCP is unavailable.

## Next Steps

- Decide on the primary cloud provider (AWS/GCP/Azure) and finalize provider configuration.
- Wire secrets and backends for Terraform remote state (e.g., S3 + DynamoDB for AWS) via GitHub environments.
- Point service repositories to the reusable CI templates herein, or move templates to a dedicated `.github` repo.