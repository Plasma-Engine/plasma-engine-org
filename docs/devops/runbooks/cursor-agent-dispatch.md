# Cursor Agent Dispatch Runbook

This document explains how the `cursor-agent-dispatch` workflow fans pull requests out to specialised Cursor agents after CodeRabbit requests changes.

## Components

- **Workflow**: `.github/workflows/cursor-agent-dispatch.yml`
- **Script**: `scripts/automation/cursor_dispatch.py`
- **Trigger**: Pull-request activity (open, sync, label changes) and manual dispatch

The automation reads the list of changed files, assigns one or more `agent:*` labels, and posts a summary table so the relevant Cursor agent (or human counterpart) knows what to tackle.

## Agent Labels

| Label | Primary Focus |
| --- | --- |
| `agent:infra` | Terraform, infrastructure modules, environment automation |
| `agent:python` | Backend services in the Python sub-repos |
| `agent:javascript` | Gateway/frontend TypeScript services |
| `agent:docs` | Markdown documentation and runbooks |
| `agent:content` | Marketing or knowledge-base content |
| `agent:ops` | Operational runbooks, playbooks, on-call artefacts |
| `agent:security` | Policies, security tooling, compliance updates |
| `agent:general` | Fallback when no specialised classifier matches |

Agents should watch for their label and push fixes until CodeRabbit reports success (which flips the coordination label to `status:coderabbit-approved`).

## Customising Classification

Set the repository variable `CURSOR_AGENT_CLASSIFIERS` to override heuristics. Supply comma-separated `prefix=label` mappings, for example:

```
CURSOR_AGENT_CLASSIFIERS=plasma-engine-content/=agent:content,docs/exa/=agent:content
```

When a file path starts with the given prefix, the corresponding label replaces the default heuristics.

## Failure Handling

- **No PR number** – Manual dispatch must supply `pr_number`; the workflow exits early otherwise.
- **Missing labels** – The script only adds labels; create them once manually or let the script add them through the GitHub API.
- **Rate limits** – Built-in retry/backoff guards against transient GitHub API errors.

## End-to-End Loop

1. PR created or updated.
2. CodeRabbit reviews; if changes are requested, `status:needs-cursor-fix` is set.
3. Dispatch workflow applies `agent:*` labels and posts a summary comment.
4. Cursor agents work the queue, push fixes, and re-request CodeRabbit using the follow-up workflow.
5. Once CodeRabbit approves, the label flips to `status:coderabbit-approved`, signalling a merge-ready state.

