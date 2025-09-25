# ADR-0003: CI/CD Bootstrap Strategy

## Status

Draft — 2025-09-25 (Pending tooling implementation)

## Context

Multiple repositories require consistent automation for linting, testing, security scanning, and deployments. Using divergent CI setups will fragment quality gates and slow releases. The solution must be accessible within private GitHub repositories and support language-specific workflows (Python, TypeScript, Terraform).

## Decision

Standardize on GitHub Actions with reusable workflows stored in `plasma-engine-infra` (or a dedicated `.github` repository). Each service repository consumes these workflows via `workflow_call`. Pipeline stages:

1. **Lint & Format**: `ruff`, `black --check`, `eslint`, `prettier --check`.
2. **Unit Tests**: Pytest, Vitest/Jest.
3. **Integration/Contract Tests**: optional matrix per repo.
4. **Security & Compliance**: `pip-audit`, `npm audit`, secret scanning, Trivy for container images.
5. **Build & Publish**: Docker images pushed to private registry; Terraform plan/apply via GitHub environments.

## Consequences

### Positive

- Single source of truth for CI configuration reduces drift.
- Reusable workflows accelerate onboarding of new repos.
- GitHub environments provide deployment approvals and secrets separation.

### Negative

- Initial setup of reusable workflows introduces upfront effort.
- GitHub Actions concurrency limits must be managed (self-hosted runners may be needed).

## Follow-Up Actions

1. Finalize runner strategy (GitHub-hosted vs. self-hosted) and budget.
2. Implement workflow templates (`lint-test.yml`, `build-publish.yml`, `terraform.yml`).
3. Document CI onboarding steps in each repo README.

