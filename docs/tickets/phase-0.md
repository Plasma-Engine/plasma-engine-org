# Phase 0 Ticket Backlog

> Format follows GitHub issue templates so background agents can pick up tasks directly. All tickets include CodeRabbit as required reviewer via repository settings.

## PE-01 — Create Plasma Engine GitHub Organization & Private Repositories

- **Repository**: `plasma-engine-infra`
- **Type**: Epic
- **Description**: Set up the `plasma-engine` GitHub organization, create the seven private repositories defined in ADR-0001, apply default branch protections, and invite core team members.
- **Tasks**:
  - [ ] Provision organization and billing
  - [ ] Create repositories with initial README + LICENSE (private)
  - [ ] Apply branch protection rules (require PR review, passing checks, signed commits)
  - [ ] Invite team (engineering, devops, product)
  - [ ] Enable CodeRabbit GitHub App organization-wide
- **Acceptance Criteria**:
  - Organization exists and is accessible
  - All repos visible to core team with protections enabled
  - CodeRabbit installed and configured

## PE-02 — Bootstrap Shared Repository Templates

- **Repository**: `plasma-engine-shared`
- **Description**: Provide reusable `.github` contents (issue templates, PR templates, CODEOWNERS, contributing guide) and publish them for reuse across all repositories.
- **Tasks**:
  - [ ] Author issue templates (`bug`, `feature`, `task`, `adr-change`)
  - [ ] Create PR template with CodeRabbit checklist
  - [ ] Define CODEOWNERS aligned to architecture leads
  - [ ] Document contribution standards (linting, commit style)
  - [ ] Set up automation to sync templates into other repos (e.g., GitHub Action or manual checklist)
- **Acceptance Criteria**:
  - Template pack merged to `main`
  - Usage instructions referenced in each repository README

## PE-03 — Configure Reusable GitHub Actions Workflows

- **Repository**: `plasma-engine-infra`
- **Description**: Implement shared workflows for lint/test/build/security/deploy per ADR-0003 and expose via `workflow_call`.
- **Tasks**:
  - [ ] Create `lint-test.yml` supporting Python & Node matrices
  - [ ] Create `build-publish.yml` (Docker build, push to GHCR)
  - [ ] Create `security-scan.yml` (Trivy, pip-audit, npm audit)
  - [ ] Create `terraform.yml` for infrastructure changes
  - [ ] Document usage in repo README and `docs/devops-process.md`
- **Acceptance Criteria**:
  - Workflows successfully triggered from sample repository (dry run)
  - Documentation updated with invocation examples

## PE-04 — Development Environment Handbook

- **Repository**: `plasma-engine-shared`
- **Description**: Publish handbook describing local setup (Docker Compose stack, secrets management, tooling) consumed by all services.
- **Tasks**:
  - [ ] Define baseline tooling requirements (Python, Node, Docker, Tilt/K8s tools)
  - [ ] Provide Compose stack with Postgres, Redis, Neo4j
  - [ ] Document `.env` management and secrets policy
  - [ ] Include troubleshooting & onboarding checklist
- **Acceptance Criteria**:
  - Handbook stored under `docs/development-handbook.md`
  - Referenced from each service README

## PE-05 — CodeRabbit Configuration Automation

- **Repository**: `plasma-engine-infra`
- **Description**: Ensure CodeRabbit automatically reviews every PR by configuring repository settings and adding `.coderabbit.yml`.
- **Tasks**:
  - [ ] Add `.coderabbit.yml` template with review rules (severity thresholds, blocking events)
  - [ ] Apply configuration to each repository (scripted or manual)
  - [ ] Update PR template checklist to include CodeRabbit pass requirement
- **Acceptance Criteria**:
  - Sample PR shows CodeRabbit review posted automatically
  - Docs updated (`docs/devops-process.md`)

## PE-06 — Repository Skeletons

- **Repository**: Each service repo
- **Description**: For each repository (`gateway`, `research`, `brand`, `content`, `agent`, `infra`, `shared`), add initial project scaffolding, README, and placeholder CI invocation.
- **Tasks**:
  - [ ] Add language-specific boilerplate (FastAPI skeleton, Next.js app, Terraform module, shared libs)
  - [ ] Reference shared workflows from ADR-0003
  - [ ] Include links back to central documentation
  - [ ] Ensure lint/test jobs succeed with placeholder tests
- **Acceptance Criteria**:
  - All repositories have non-empty `main` branch with building CI
  - README includes status badges and next steps

## PE-07 — Program Project Board & Automation

- **Repository**: `plasma-engine-infra`
- **Description**: Create GitHub Project board for Plasma Engine, define columns, automation rules, and integrate with issues/PRs.
- **Tasks**:
  - [ ] Create project board with columns (Backlog, In Progress, Review, Done, Blocked)
  - [ ] Configure automation to move issues/PRs based on status
  - [ ] Document usage guidelines
- **Acceptance Criteria**:
  - Project board live and accessible via README
  - Issues automatically move based on linked PR state

