 # Activity Log

 > Daily build log of DevOps stack work. Include commands, outputs, artifacts, open questions, and dependencies.

 ## 2025-09-25

 - Files touched:
   - `docs/devops/README.md` (new)
   - `docs/devops/activity-log.md` (new)
  - `plasma-engine-infra/infra/terraform/**` (modules: networking, compute, storage, iam, observability, security; envs/dev wiring)
  - `.github/workflows/**` (reusable-* and ci.yml)
  - `ci/actions/**` (build, test, security, package, deploy, rollback)
  - `docs/devops/playbooks/**` (build, test, security, package, deploy, rollback)
  - `docs/devops/runbooks/**` (incident-response, oncall-quickstart)
  - `docs/devops/release/checklist.md`
  - `docs/exa/**` (README, schemas/openapi.json, examples/sample-query.json)
  - `scripts/**` (onboarding.sh, local-test.sh, deploy.sh, research_exa.py)
 - Commands run:
   - `git status -sb` — verified working branch
   - `python3 --version`, `node --version`, `npm --version` — verified toolchain
   - `mkdir -p docs/devops/{playbooks,runbooks,release} docs/exa` — initialized docs structure
  - Scripts: `scripts/onboarding.sh`, `scripts/local-test.sh`
  - Validation:
    - Ruff: not installed (skipped)
    - Black: not installed (skipped)
    - Pytest: not installed (skipped)
    - ESLint: config missing (skipped)
    - Terraform: not installed (skipped)
 - Current branch: `cursor/setup-full-devops-stack-and-workflows-3f5e`
 - Tooling present: Python 3.13.3, Node v22.16.0, npm 10.9.2
 - Tooling missing: Terraform (terraform fmt/apply unavailable), pipx, poetry
 - Blockers / notes:
   - Rube MCP not accessible in this environment. Falling back to local knowledge and will insert `# TODO:` to validate against Rube MCP later.
   - Web search tool returned non-authoritative summaries without URLs. `# TODO:` Replace placeholder references with authoritative links via Rube MCP.
   - Subprojects (`plasma-engine-*`) not present in current workspace snapshot. `# TODO:` Confirm full monorepo checkout and paths before wiring service-specific CI.
 - Next actions:
   - Scaffold Terraform module directories and environment (`plasma-engine-infra/infra/terraform/...`).
   - Create CI/CD workflows in `.github/workflows/` that reference `ci/` composites.
   - Author runbooks, release checklists, and SOPs aligned to the automation.
   - Mirror Exa API schemas and example queries into `docs/exa/`.
  - Add ESLint config and tighten CI gates; install Terraform in CI runners.
 - Dependencies needed from other agents:
   - Security: Approved baseline controls for IAM, networking, and secrets management.
   - Platform: Cloud provider choice and org/account IDs, naming conventions, regions.
   - Research: Confirm Exa API versions/models to mirror.

- Autopilot upgrade (2025-09-25): Added `.github/workflows/autopilot.yml` and
  `scripts/automation/autopilot_orchestrator.py` so Cursor agents, CodeRabbit,
  and GitHub merges run on autopilot. Documented the loop in
  `docs/devops/runbooks/autopilot.md`. Next: configure
  `vars.AUTOPILOT_REQUIRED_STATUS_CONTEXTS` once full CI gates stabilize.
- Autopilot localisation (2025-09-25): Adjusted orchestrator to reuse
  `coderabbit_follow_up` without direct dataclass construction, documented PAT
  requirements for local runs, and cleaned `__pycache__` artifacts after manual
  Python execution attempts.


