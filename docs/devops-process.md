# Plasma Engine DevOps Process

## Branching & Release Strategy

- **Default branch**: `main` (protected). All feature work occurs on short-lived branches named `<repo>/<issue-id>-brief-description` (e.g., `gateway/PE-12-bootstrap-fastapi`).
- **Release branches**: Created per service as needed (`release/<version>`). Hotfix branches stem from the latest release tag (`hotfix/<issue-id>`).
- **Versioning**: Semantic versioning per repository. Tags managed via GitHub Actions release workflows.

## Issue & Ticket Workflow

1. Create issue using standard template (see `docs/tickets/phase-0.md`).
2. Assign owner, labels (`phase-0`, service-specific label, `needs-review`).
3. Link issue to GitHub Project board column (Backlog → In Progress → Review → Done).

## Pull Request Requirements

- Reference issue ID in PR title (`[PE-12] Gateway bootstrap`).
- Include checklist: tests run, lint pass, docs updated, ADR impact.
- **Automated reviews**: Enable CodeRabbit for all repositories. Every PR must receive CodeRabbit review plus one human approver.
- Require status checks: lint, tests, security scan, CodeRabbit summary.

## Continuous Integration

- Shared reusable GitHub Actions workflows (see ADR-0003) invoked via `workflow_call`.
- Stages: Lint → Test → Build → Security → Package/Deploy → Notify.
- Publish artifacts to private registry (`ghcr.io/plasma-engine/*`).

## Continuous Delivery

- Deploy to staging automatically after merge to `main`. Production deploys require manual approval via GitHub environments.
- Terraform plans gated by `infra` approvals.
- Rollbacks handled via Helm release history (Kubernetes) and IaC state reverts.

## Observability & Alerts

- Standard logging format (JSON) with correlation IDs.
- Metrics exposed via OpenTelemetry; alerts configured in Grafana/Prometheus.
- Incidents tracked via GitHub Issues labeled `incident` and linked to postmortems.

## Quality Gates

- Minimum 80% test coverage for new modules; coverage enforced via CI.
- Dependency updates managed by Renovate bot with weekly batch PRs.
- Security scans (Trivy, pip-audit, npm audit) mandatory before merge.

## Tooling Checklist per Repository

- CODEOWNERS with architecture and domain leads.
- Issue templates (`bug`, `feature`, `task`, `adr-change`).
- PR template with CodeRabbit instructions.
- Branch protection rules: require signed commits, linear history, passing checks.

## Communication

- Weekly status sync referencing Project board metrics.
- Async updates posted to shared Slack channel `#plasma-engine-devops`.
- All ADR proposals announced via GitHub Discussions.
