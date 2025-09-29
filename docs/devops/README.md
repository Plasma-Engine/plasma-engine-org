<!--
Explainer: This README orients DevOps contributors to the operational
documentation that pairs with our automation. Every section links to
actionable runbooks, SOPs, and release materials. Inline TODOs indicate
organization-specific inputs still required.
-->

# DevOps Handbook (Operational)

## Contents
- Overview and Principles
- Playbooks (how-to procedures)
- Runbooks (incident/operational response)
- Release and Change Management
- Activity Log (daily build logs)

## Overview and Principles
We adopt automation-first operations with Infrastructure-as-Code (IaC),
immutable builds, and environment parity. Observability and security are
first-class; changes are auditable via CI/CD and GitHub environments.

## Playbooks
See `docs/devops/playbooks/` for task-oriented, step-by-step guides.
- Provisioning infra
- CI/CD operations
- Secrets management
- Observability setup

## Runbooks
See `docs/devops/runbooks/` for structured response procedures.
- Service outage
- Degraded performance
- Failed deploy and rollback
- Security incident

## Release and Change Management
See `docs/devops/release/` for checklists and approvals.
- Release checklist
- Change request template
- Post-release validation

## Activity Log
See `docs/devops/activity-log.md` for daily logs of changes, commands,
artifacts, open questions, and next actions.

## References
- ADRs: `docs/adrs/`
- DevOps Process: `docs/devops-process.md`
- Exa API references: `docs/exa/`  
  # TODO: Confirm Exa API versions and auth scheme with platform team.

