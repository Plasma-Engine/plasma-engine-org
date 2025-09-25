# Playbook: Deployment

Purpose: Describe deployment flow for staging and production environments.

Inputs:
- Commit SHA / release tag
- Environment (`staging`, `production`)
- Image registry credentials (GitHub Container Registry)

Outputs:
- Deployed application state
- Links to CI runs and artifacts

Steps:
1. Validate release readiness using `docs/devops/release/checklist.md`.
2. Trigger `Release` workflow to build and publish images.
3. Approve deploy to `staging` environment in GitHub.
4. Validate health checks and dashboards.
5. Approve deploy to `production` environment.

References:
- GitHub Actions environments and approvals
- Terraform/Helm charts (TODO: link when added)

TODO: Parameterize smoke tests and SLO gates.

