<!--
Explainer: This README orients contributors to the DevOps standards for Plasma Engine.
It links playbooks, runbooks, release processes, and CI/CD policy. Inline TODOs
flag organization-specific inputs still needed.

Authoritative references:
- ADR-0003 CI/CD Bootstrap (see `docs/adrs/ADR-0003-ci-cd-bootstrap.md`)
- DevOps process overview (see `docs/devops-process.md`)

# TODO: Confirm owning team(s) and escalation contacts for DevOps standards.
-->

## DevOps Standards and Index

- Playbooks: `docs/devops/playbooks/`
- Runbooks: `docs/devops/runbooks/`
- Release: `docs/devops/release/`
- Activity Log: `docs/devops/activity-log.md`

## Pipelines (high level)

1. Lint → Test → Build → Security → Package → Deploy → Verify → Notify
2. Reusable GitHub Actions workflows live in this repo and are consumed by service repos via `workflow_call`.
3. Environments: dev → staging → prod with gated approvals in GitHub Environments.

## Observability

- Logging: JSON logs with correlation IDs.
- Metrics/Tracing: OpenTelemetry; dashboards in Grafana; alerts in Prometheus.

## Security

- SBOM generation prior to release.
- Image scanning (Trivy) and dependency audits (pip-audit, npm audit).
- Least privilege IAM for CI/CD and runtime.

## How to Use This Directory

- Start with playbooks for “how to” guidance.
- Use runbooks during operations and incidents.
- Follow release checklists for cutovers and rollbacks.

# TODO: Link internal wiki/confluence pages if applicable.

