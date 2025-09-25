<!--
Explainer: Centralized daily devops activity log for transparency and handoffs.
Log concrete command outputs (with sensitive data redacted), decisions, blockers, and next steps.
Entries should be append-only, newest first.
-->

## 2025-09-25

### Shell & Repo Initialization
- Working directory: `/workspace` (absolute user path unavailable in this environment).
- Git status: on branch `cursor/scaffold-project-infrastructure-and-automation-5ad7`, remote configured. [redacted tokens]

### Research Sync
- Created `docs/devops/README.md` and initialized this activity log.
- `docs/exa/` not yet present; will scaffold with Exa API schemas (JSON/YAML) and summaries.

### Decisions
- Defaulted to local web search due to Rube MCP unavailability in this environment. Will replace findings via Rube MCP in next pass.
- Use root `infra/terraform/` for organization-level starters. Team-specific stacks can live under `plasma-engine-infra/` until consolidation.

### Blockers / TODOs
- TODO(research@plasma): Pull authoritative Exa API schemas via Rube MCP; replace placeholders.
- TODO(infra@plasma): Select and configure remote Terraform state backend and credentials.
- TODO(security@plasma): Provide non-privileged CI tokens; rotate any exposed tokens immediately.

### Next Steps
- Scaffold `docs/exa/` with endpoint placeholders and citations.
- Add `infra/terraform/` starters with provider/version pins and comments.
- Add `ci/` templates and `scripts/` helpers; run `ruff`, `black`, `eslint` and record outputs here.

### Lint/Format and Infra Bootstrap
- Lint summary (scripts/lint-all.sh):
  - [lint-all] Python: ruff -> WARN: not installed
  - [lint-all] Python: black --check -> WARN: not installed
  - [lint-all] JS/TS: eslint -> WARN: not installed
  - Summary: PY_STATUS=2 JS_STATUS=2
- Format summary (scripts/format-all.sh):
  - [format-all] WARN: black not installed; no changes made
- Terraform bootstrap (scripts/bootstrap-infra.sh):
  - ERROR: terraform CLI not found

Recommendations:
- TODO(devx@plasma): Add dev-tool bootstrap: `pip install ruff black` and `npm i -g eslint` (or project-local devDeps) for contributors; codify in CI.
- TODO(infra@plasma): Install Terraform CLI (>= 1.5) locally and in CI runners; consider using `tfenv` or `asdf`.

### Code Review Automation
- Branch pushed: `chore/devops-scaffold-exa-ci-terraform`
- Attempted PR creation via GitHub API failed (HTTP 404) likely due to token scope limits in this environment.
- Manual PR link (from push output):
  - https://github.com/Plasma-Engine/plasma-engine-org/pull/new/chore/devops-scaffold-exa-ci-terraform
- Next action: Open PR and comment `@coderabbitai review` to trigger CodeRabbit. If the app is not installed, install org-wide and retry.

