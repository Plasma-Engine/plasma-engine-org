<!--
Explainer: CI/CD playbook. Describes how to use reusable workflows, environments,
and common parameters. Links to runbooks for incidents and rollbacks.
-->

## Reusable Workflows

- Lint/Test/Build/Security/Package/Deploy/Rollback under `.github/workflows/*`.
- Consumed via `workflow_call` by service repos.

## Inputs

- `service_name`, `environment`, `image_tag`, `deploy_strategy`.

## Outputs

- Build artifacts, images in GHCR, deployment status.

# TODO: Document environments and protection rules.

