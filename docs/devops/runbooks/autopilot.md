# Autopilot Orchestrator Runbook

This runbook documents the fully automated loop that coordinates Cursor
specialists, CodeRabbit reviews, and GitHub merges so the repository can build
itself end-to-end with minimal human intervention.

## Components

- **Workflow**: `.github/workflows/autopilot.yml`
- **Script**: `scripts/automation/autopilot_orchestrator.py`
- **Dependencies**: `scripts/automation/coderabbit_follow_up.py`, `scripts/automation/cursor_dispatch.py`

## High-Level Flow

1. **Schedule / manual trigger** – The workflow runs hourly via cron or on
   demand through `workflow_dispatch`. Optional inputs allow a dry run or
   alternate merge settings.
2. **CodeRabbit sync** – The orchestrator imports
   `coderabbit_follow_up.process_pull_requests`, ensuring status labels stay in
   lock-step with CodeRabbit reviews and that `@coderabbit review` is re-issued
   whenever the head commit changes.
3. **Cursor dispatch** – Pull requests carrying `status:needs-cursor-fix`
   receive updated `agent:*` labels (via the shared classifier) plus a summary
   comment so the appropriate Cursor agent wakes up with full context.
4. **Automerge on green** – When a pull request carries the
   `status:coderabbit-approved` label and all required status checks report
   success, the orchestrator merges the branch into the configured target
   (default `main`). Merge method defaults to `squash` but can be overridden via
   workflow input.

## Configuration Knobs

| Variable | Purpose |
| --- | --- |
| `AUTOPILOT_TARGET_BRANCH` | Branch that receives autopilot merges (default `main`). |
| `AUTOPILOT_MERGE_METHOD` | GitHub merge strategy: `squash`, `merge`, or `rebase`. |
| `AUTOPILOT_DRY_RUN` | When `true`, the orchestrator prints intended actions without mutating GitHub state. |
| `AUTOPILOT_REQUIRED_STATUS_CONTEXTS` | Optional comma-separated list of CI status contexts that must report success before a merge. |
| `CURSOR_AGENT_CLASSIFIERS` | Overrides for Cursor agent label inference (re-used from the dispatch script). |
| `CODERABBIT_LOGINS` | Additional CodeRabbit reviewer identities, mirroring other workflows. |

## Safety Considerations

- Merges only occur when CodeRabbit approval is present and the combined status
  API reports `success`. Optional contexts provide extra guardrails for critical
  jobs (for example, integration or security gates).
- Dry runs allow operators to inspect planned actions in production without
  touching open pull requests.
- All API calls use the built-in GitHub token, so the workflow respects
  repository-scoped permissions. If stricter controls are required, create a
  fine-grained PAT with limited scopes and store it in `secrets.AUTOPILOT_TOKEN`
  before updating the workflow.

## Troubleshooting

- **No agent labels appear** – Confirm `CURSOR_AGENT_CLASSIFIERS` is set at the
  repository level and that the GitHub token has access to modify labels.
- **Automerge skipped** – Check the workflow logs for the orchestrator output;
  the JSON report lists the reason (missing status context, draft PR, base
  branch mismatch, etc.).
- **Repeated dispatch comments** – The orchestrator only posts when labels
  change. If comments appear on every run, ensure external tooling is not
  clearing the `agent:*` labels between cycles.
- **Local execution fails with `404`** – The default GitHub CLI token only has
  access to repositories owned by the authenticated user. Export a PAT or fine-
  grained token with read/write access to `Plasma-Engine/plasma-engine-org`
  before running `python3.11 -m scripts.automation.autopilot_orchestrator`.


