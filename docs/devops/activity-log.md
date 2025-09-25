<!--
Explainer: Rolling activity log for DevOps work. Append under a dated H2 section.
Capture commands, outputs, artifacts, unresolved issues, next actions, and dependencies.
-->

## 2025-09-25

- Context: Full-Build Background Agent run to scaffold infra, CI/CD, docs, and scripts.
- Repo branch: # TODO: fill in current branch name from `git rev-parse --abbrev-ref HEAD`.
- External lookups: Rube MCP unavailable in this environment; fell back to generic guidance.
  - # TODO: A follow-up agent should query Rube MCP for Exa API and compliance specs.

### Changes
- Added `docs/devops/README.md` (DevOps standards index).
- Created this log file to track ongoing work.
- Added playbooks (`ci-cd`, `terraform`, `security`, `observability`) and runbooks (`incident-response`, `rollback`, `oncall-handover`).
- Added release checklist (`docs/devops/release/RELEASE-CHECKLIST.md`).
- Scaffolded Terraform modules under `plasma-engine-infra/infra/terraform` (networking, compute, storage, iam, observability, security) with explainers and TODOs; wired `envs/dev` composition.
- Created reusable CI workflows: `python-ci`, `node-ci`, `terraform-ci`, `security-scan`, `build-and-push`, `deploy`, `rollback`.
- Added developer scripts: `onboard_dev.sh`, `run_python_ci_local.sh`, `run_node_ci_local.sh`, `terraform_validate.sh`, `deploy.py`, `exa_research.py`.
- Created Exa docs scaffold under `docs/exa/` (`README.md`, `auth.md`).

### Commands & Outputs (selected)
- Tooling audit: Python and Node present; Terraform, ruff/black/pytest/eslint/tflint/pre-commit missing locally.
  - # TODO: Add local setup instructions and CI-side tool pins.

- Onboarding check

  ```
  Checking core tooling...
  # TODO: Install Terraform >=1.6
  # TODO: pipx install ruff
  # TODO: pipx install black
  # TODO: pipx install pytest
  # TODO: npm i -g eslint
  # TODO: Install tflint
  # TODO: pipx install pre-commit
  Onboarding check complete. See docs/devops/README.md for standards.
  ```

- Terraform validate (dev env)

  ```
  scripts/terraform_validate.sh: line 9: terraform: command not found
  ```

### Unresolved Issues / Dependencies
- Need authoritative Exa API schemas and auth flow from exa.ai docs.
- Need org decisions for environments, cloud provider, and IAM patterns.
- CI environments and secrets (e.g., `EXA_API_KEY`, cloud creds) must be set in GitHub Environments.

### Next Actions
- Scaffold playbooks, runbooks, release checklists.
- Add Terraform module skeletons with TODO placeholders.
- Add reusable CI workflows and developer scripts.
- Populate `docs/exa/schemas/` and `docs/exa/examples/` with official content via Rube MCP.
- Configure GitHub Environments and required secrets; enable required status checks per `docs/devops-process.md`.


