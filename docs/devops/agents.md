# Plasma Engine Background Agents Guide

> All agents run from `/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org`. Default to Rube MCP for any external lookup (docs, APIs, repos) before falling back to local shell tooling such as `exa`, `curl`, or GitHub CLI. Each deliverable must include top-of-file explainers, exhaustive inline comments, explicit TODOs with owners/context, and must append a dated log entry to `docs/devops/activity-log.md`.

## Planning & Research Agent (Agent A)
- Map the entire DevOps lifecycle (Plan → Monitor) specific to our architecture. 
- Inventory the current repository structure via `exa -1 --classify --long --git --recurse .` and document findings. 
- Source best practices from CNCF, AWS, Google SRE, and DORA; capture authoritative URLs and summaries. 
- Review `https://exa.ai/docs` (CLI + API) and extract schema/usage guidance for later agents. 
- Deliver a research brief tailored to our stack and compliance requirements.

## Tooling & API Docs Agent (Agent B)
- Fetch Exa API documentation (REST + SDK) via MCP or, if required, local tooling; store raw docs in `docs/exa/`. 
- Document authentication, rate limits, and query syntax; produce a quick-reference Markdown with inline comments. 
- Locate official GitHub repos/examples (prefer MCP + `exa`); vendor critical snippets into `third_party/exa/` with attribution. 
- Flag missing schemas or unclear APIs for follow-up in the activity log.

## Infrastructure Blueprint Agent (Agent C)
- Digest Agent A’s research brief and design target-state architecture diagrams/IaC skeletons. 
- Populate `infra/terraform/` with module scaffolds (networking, compute, observability, security) featuring inline explainers. 
- Define modular CI/CD pipeline stages and observability stack requirements, referencing best-practice sources. 
- Capture assumptions and pending decisions in the activity log.

## Implementation Standards Agent (Agent D)
- Audit current repo conventions and produce exhaustive coding/testing/release standards. 
- Draft Python/TypeScript guidelines with detailed comments and rationales. 
- Define testing matrices, branching strategy, and security policies (SAST/DAST, dependency governance). 
- Integrate incident response procedures aligned with industry benchmarks.

## Enablement & Automation Agent (Agent E)
- Convert all agent outputs into modular SOPs/checklists covering the entire DevOps loop. 
- Embed references to stored Exa docs and tooling commands. 
- Identify automation candidates (background agents, GitHub Actions, Rube workflows) and build a prioritized backlog. 
- Recommend KPIs (DORA metrics, retrospectives) to sustain continuous improvement.

## Execution Agent — Infrastructure & Automation Seed
- Transform the blueprint into actionable artefacts: jump-start `infra/terraform/`, `ci/`, and `scripts/` with heavily commented starters. 
- Mirror Exa API schemas locally (JSON/YAML) with clear field explanations and source URLs. 
- Run lint/format commands as files are created and log command output, blockers, and next steps.

## Execution Agent — Best Practices Codifier
- Expand `docs/devops/playbooks/` with lifecycle-aligned playbooks citing CNCF/AWS/DORA references. 
- Produce commented templates (`CONTRIBUTING.md`, `SECURITY.md`, `RELEASE_CHECKLIST.md`) including TODO placeholders. 
- Store sourced examples/schemas under `third_party/references/` with attribution using MCP/`exa`. 
- Update the activity log with sourced materials and open questions.

## Execution Agent — Observability & SRE Implementation
- Extend infrastructure skeleton with observability modules in `infra/observability/`. 
- Write runbooks for alert responses in `docs/devops/runbooks/`, detailing trigger conditions and escalations. 
- Draft scripts for bootstrapping dashboards/alerts; ensure extensive explainers within each file. 
- Log validation steps and follow-ups in the activity log.

## Execution Agent — Security & Compliance Automation
- Implement CI security stages under `ci/security/` with annotated YAML pipelines. 
- Create policy-as-code samples (OPA/Conftest) in `infra/policy/` with commentary plus references (NIST, OWASP). 
- Mirror security-related Exa/GitHub schemas into `docs/exa/security/`. 
- Record executed scans, issues, and next actions in the activity log.

## Execution Agent — Developer Experience & Tooling
- Scaffold onboarding scripts in `scripts/devx/` covering environment setup, local testing, and Exa integration. 
- Produce IDE/linter configs with inline rationale. 
- Configure automated background-agent workflows (GitHub Actions/Rube pipelines) describing triggers, inputs, outputs. 
- Document friction points and mitigation ideas in the activity log.

## Execution Agent — QA & Release Validation
- Build testing harnesses (unit/integration/e2e) with thoroughly commented Python/TypeScript files. 
- Define release gating workflows in `ci/release/` (artifact promotion, approvals, rollback). 
- Author verification checklists in `docs/devops/release/`, mapping each to metrics/KPIs. 
- Store annotated release workflow examples in `third_party/references/releases/` and log validation status.

## Background Agent — Coding Kickoff
- Sync research materials (`docs/devops/README.md`, `docs/exa/`, `docs/devops/activity-log.md`) and note blocking TODOs. 
- Begin scaffolding infrastructure, CI/CD, and scripts with comprehensive comments and TODO markers. 
- Mirror Exa API schemas into `docs/exa/` and cite sources. 
- Run lint/formatters early and log all commands, outputs, blockers, and next steps.

## Background Agent — Parallel Research & Documentation
- Expand playbooks/runbooks/release docs with modular, source-cited Markdown across `docs/devops/`. 
- Use MCP→`exa` to gather exemplars, storing raw references under `third_party/references/` with attribution. 
- Produce Exa quick-reference guides (auth, queries, rate limits) in `docs/exa/`. 
- Summarize materials gathered and open questions in the activity log.

## Background Agent — Full Build Implementation
- Execute an end-to-end build: fully flesh out Terraform modules, CI/CD workflows, runbooks, SOPs, and developer tooling scripts. 
- Mirror complete Exa API schemas and usage patterns into `docs/exa/`. 
- Continuously lint/test (`ruff`, `black`, `pytest`, `eslint`, `terraform fmt`, etc.) and document outcomes. 
- Add a detailed daily build log with files touched, commands run, produced artefacts, unresolved issues, and next steps.

## Repository Focus Guidance
- Prioritize `plasma-engine-gateway` for full build-out first (tickets PE-101 → PE-103 unlock all dependent services). 
- Apply the “Full Build Implementation” prompt to this repo, ensuring progress is logged in `docs/devops/activity-log.md` and `# TODO:` markers highlight remaining work.
