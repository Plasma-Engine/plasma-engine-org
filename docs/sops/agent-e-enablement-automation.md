### Agent E Enablement & Automation SOP (Plan → Monitor)

Purpose: Ensure a repeatable “always works” delivery process across all Plasma Engine services by standardizing plan-build-release-operate-monitor activities, with actionable checklists, runbooks, and automation hooks.

Scope: Applies to all repos (`gateway`, `research`, `brand`, `content`, `agent`, `shared`, `infra`). Aligns with ADRs and the DevOps process guide.

Related references
- ADRs: `docs/adrs/ADR-0001-multi-repo-structure.md`, `docs/adrs/ADR-0002-platform-tech-stack.md`, `docs/adrs/ADR-0003-ci-cd-bootstrap.md`
- DevOps: `docs/devops-process.md`, tickets under `docs/tickets/*`
- Exa knowledge base (stored references)
  - exa://plasma-engine/phase-1-overview
  - exa://plasma-engine/ci-cd-standards
  - exa://plasma-engine/service-guides
- RUBE MCP config: `config/rube/mcp-config.json` (use `config/rube/mcp-config.template.json` as a bootstrap if missing)

---

### 1) Plan

Objectives
- Clarify scope, success criteria, risk, and dependencies.
- Create or link to the tracking artifact (Issue, ADR, or ticket).

Inputs/Outputs
- Inputs: Product brief, ADR proposals, Phase tickets under `docs/tickets/`.
- Outputs: Issue created and triaged, acceptance criteria, initial test approach, CI impacts noted.

Checklist (Plan)
- Create issue with template and labels. See `docs/tickets/issue-template.md`.
- Link to relevant ADR(s) and Phase docs (`docs/tickets/phase-*.md`).
- Define acceptance criteria and minimal test plan.
- Identify CI/CD changes (if any) and security implications.
- Update project board (Backlog → In Progress when work starts).

Tooling commands
```bash
make help | cat
```

Runbooks
- See `../runbooks/bootstrap-new-service.md` when work introduces a new repo/service.

---

### 2) Design

Objectives
- Produce a solution design referencing ADRs and Exa docs; validate constraints.

Checklist (Design)
- Check for ADR conflicts or required updates.
- Capture non-functional requirements (latency, cost, security, SLOs).
- Define observability signals (logs, metrics, traces) to be added.
- Decide schema and API changes and compatibility plan.

References
- ADR-0002 for tech stack and conventions.
- Exa: exa://plasma-engine/service-guides

---

### 3) Build

Objectives
- Implement changes with tests, docs, and automation hooks.

Checklist (Build)
- Write unit and contract tests; target ≥80% coverage (see `docs/devops-process.md`).
- Keep changes small; follow branch naming from DevOps guide.
- Update README or API docs as needed.
- Add or adjust reusable CI workflow usage per ADR-0003.

Tooling commands
```bash
# Python repos
pytest -q

# Node/TypeScript repos (gateway)
npm test --silent | cat

# Lint all (from org root if sub-repos are present)
make lint-all
```

Checklists
- See `../checklists/engineering-pr-checklist.md` before opening a PR.

---

### 4) Verify

Objectives
- Ensure code quality gates pass locally and in CI; peer review + automated review.

Checklist (Verify)
- Run tests locally and verify linters.
- Open PR referencing the issue; include PR checklist.
- Ensure CI jobs cover: Lint → Test → Security → Build.
- Address CodeRabbit and human review feedback.

Tooling commands
```bash
make test-all
```

---

### 5) Release

Objectives
- Safely package and deploy to staging, then promote to production with approvals.

Checklist (Release)
- Merge to `main` triggers staging deploy via reusable workflows.
- Create and push version tags if required by release process.
- Obtain manual approval for prod via GitHub Environments.
- Prepare rollback plan and verify health checks.

Tooling commands
```bash
# Org-level helpers (when sub-repos are present)
make build-all
make push-all

# Tag release across repos interactively
make tag-release
```

Runbooks
- `../runbooks/rollback.md`
- `../runbooks/ci-cd-pipeline-fix.md`

---

### 6) Operate

Objectives
- Ensure services meet SLOs; handle incidents and maintenance.

Checklist (Operate)
- Standard JSON logging with correlation IDs (see DevOps guide).
- OpenTelemetry metrics exposed and scraped; dashboards available.
- On-call rotation documented; escalation path clear.
- Known operations documented in runbooks.

Runbooks
- `../runbooks/incident-response.md`
- `../runbooks/infra-terraform-apply.md`

---

### 7) Monitor

Objectives
- Track KPIs and DORA metrics; drive continuous improvement.

Checklist (Monitor)
- Review `../monitoring/kpis.md` thresholds and alerts.
- Record incidents with labels and link postmortems.
- Schedule retrospectives and backlog improvements.

Tooling commands
```bash
# Infra visibility (if docker-compose infra is running)
make ps
make logs
```

Feedback loops
- Weekly review of KPIs and DORA metrics.
- Monthly retrospective; update `../backlog/automation.md` priorities.

---

### Automation Hooks Map

- GitHub Actions reusable workflows: see ADR-0003. Pipelines: Lint → Test → Security → Build/Publish → Deploy → Notify.
- RUBE workflows (MCP): codify SOP steps as commands; expose checklists and runbooks in the MCP menu.
- Background agents (Agent E):
  - Watch PRs for checklist compliance and missing artifacts.
  - Nudge owners when runbooks are referenced but not updated.
  - Open issues for detected toil and propose automation.

See `../backlog/automation.md` for prioritized items.

---

### RACI (Lightweight)

- Responsible: Feature owner (per repo), On-call (Operate/Monitor)
- Accountable: Repo CODEOWNERS
- Consulted: Platform/Infra
- Informed: Product/Stakeholders

