### Automation Backlog (Prioritized)

P0 — Immediate
- Reusable GitHub Actions: `lint-test.yml`, `build-publish.yml`, `terraform.yml` (ADR-0003)
- Enforce PR checklist via status check (Agent E + GitHub App)
- Security scans (pip-audit, npm audit, Trivy) as required checks
- Auto-labeler for PRs by path (gateway/research/…)

P1 — Near-term
- Background Agent E: comment on PRs with missing tests/docs/observability
- Renovate bot configuration across repos; weekly batch windows
- Release tagging automation and changelog generation
- RUBE MCP: expose SOP checklists and runbooks as executable commands

P2 — Mid-term
- Flake detector for CI (retry and quarantine policy)
- Coverage reporter with threshold gate and trends dashboard
- Drift detection for Terraform (nightly `terraform plan` in dry-run)
- Incident helper: template issue creation + timeline capture bot

P3 — Exploratory
- Performance budgets with automated regression alerts
- Dependency supply chain risk scoring dashboard
- Self-hosted runners autoscaling

Cross-cutting owners
- CODEOWNERS enforceable review gates
- Platform/Infra maintain reusable workflows
- Each repo maintains service-specific jobs and secrets

References
- ADR-0003 CI/CD bootstrap
- Exa: exa://plasma-engine/automation-roadmap

