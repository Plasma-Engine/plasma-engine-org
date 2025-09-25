<!--
Explainer: Rollback procedure for failed deployments.
-->

## Prerequisites

- Identify failing version and target rollback version
- Access to deployment system and IaC state

## Steps

- Halt forward deploys
- Rollback application (e.g., Helm rollback)
- Revert IaC if needed
- Validate health checks and dashboards
- Communicate resolution

