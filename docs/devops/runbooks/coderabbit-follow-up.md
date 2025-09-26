# CodeRabbit Follow-Up Runbook

This runbook explains how the `coderabbit-follow-up` automation keeps pull requests in the `plasma-engine-org` umbrella moving without human babysitting.

## Overview

- **Workflow**: `.github/workflows/coderabbit-follow-up.yml`
- **Script**: `scripts/automation/coderabbit_follow_up.py`
- **Cadence**: Every 30 minutes, on every pull-request update, and after each CodeRabbit review event

The workflow reads CodeRabbit review activity and applies status labels so other agents (or humans) know whether a PR needs a fresh review, needs fixes, or is ready for merge.

## Status Labels

| Label | Meaning | Intervention |
| --- | --- | --- |
| `status:needs-coderabbit-review` | CodeRabbit has not reviewed the latest head commit. The automation re-requests a review immediately. | Wait for CodeRabbit to respond. |
| `status:needs-cursor-fix` | CodeRabbit requested changes on the latest commit. | Cursor agents (or humans) should address the feedback and push updates. |
| `status:coderabbit-approved` | CodeRabbit approved the current head commit. | Merge or run final validation gates. |

## Customising CodeRabbit Identities

By default, the script recognises the GitHub logins `coderabbitai[bot]` and `coderabbitai`. To add aliases (for self-hosted installations, for example), define a repository variable named `CODERABBIT_LOGINS` with a comma-separated list of additional logins.

## Failure Modes

- **Missing labels** – The script bootstraps labels automatically; no manual setup is required.
- **Rate limits** – Exponential backoff keeps the job within GitHub API quotas. If limits are repeatedly hit, reduce the schedule frequency.
- **Unexpected review state** – Any state other than `APPROVED` or `CHANGES_REQUESTED` falls back to `status:needs-coderabbit-review` to keep the pipeline conservative.

## Extending the Autopilot Loop

The JSON summary printed by the script can be parsed by subsequent workflow steps or external observers (for example, a Cursor background agent) to trigger follow-on tasks such as opening issues, syncing project boards, or dispatching further automation.

