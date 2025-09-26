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

### Autonomous Review Loop

- `coderabbit-follow-up` workflow continually requests CodeRabbit reviews, flips coordination labels, and ensures the latest commit is analysed. See `docs/devops/runbooks/coderabbit-follow-up.md` for operating details.
- `cursor-agent-dispatch` workflow classifies changed files and applies `agent:*` labels so specialised Cursor agents can address feedback. The runbook lives at `docs/devops/runbooks/cursor-agent-dispatch.md`.
- Cursor agents should watch for their label, push fixes, and re-run CodeRabbit until `status:coderabbit-approved` appears, signalling merge readiness.

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

## Rube MCP Integration

The Plasma Engine program standardises on [Rube MCP](https://rube.app/mcp) for accessing external services (Slack, Google Workspace, GitHub, etc.) so that individual repositories do **not** need to maintain separate API tokens.

### Install & Authenticate Rube

1. Install the CLI (`brew install rube-cli` or download from the Rube site).
2. Sign in via the Rube desktop/web app and connect the integrations required by Plasma Engine (Slack, Gmail, Drive/Sheets, GitHub, …).
3. Generate an MCP configuration in **Settings → MCP**; this produces JSON describing the available tools and required environment variables.

### Repository Configuration

- A template lives at `config/rube/mcp-config.template.json`. Copy it to `~/.config/rube/mcp-config.json`, substitute your real secrets, and prune/extend the `connections` array as needed.
- In Cursor / VS Code, open **Settings → MCP Servers** and add the same JSON. Keep the server ID `rube` so scripts and agents can reference it consistently.
- For background agents, launch with `RUBE_MCP_CONFIG=~/.config/rube/mcp-config.json rube mcp …` (or follow the instructions in the Rube docs) so they inherit the shared connections.

### GitHub Secrets & Formatting

- Store long‑lived keys in **Settings → Secrets and variables → Actions** at the organisation level. Use uppercase names without quotes, e.g. `RUBE_API_KEY`, `RUBE_WORKSPACE`, `RUBE_DEFAULT_CONNECTIONS`.
- Per-environment overrides should go into environment secrets (`staging`, `production`) so workflows can set different Rube workspaces if required.
- Workflows that call Rube must export the key explicitly: `env: { RUBE_API_KEY: ${{ secrets.RUBE_API_KEY }}}` before invoking `rube mcp call …`.

### Operational Notes

- Rube handles OAuth refresh internally; you do **not** need to store Google Drive/Sheets bearer tokens separately.
- After adding a new integration in Rube, regenerate the config JSON and update the template if the connection list changes.
- Troubleshoot by running `rube mcp tools` locally—if the tool appears there, Cursor/agents can access it once the config is refreshed.

