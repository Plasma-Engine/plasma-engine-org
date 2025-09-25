# Deployments Runbook

Purpose: Standardize deployments across environments with preflight validations and clear rollback instructions.

## Preflight
- [ ] CI green on main
- [ ] Security gates passed (SARIF reports triaged)
- [ ] Version/tag prepared and changelog reviewed

## Staging Deploy
- [ ] Execute `ci/deploy.yaml` for `staging`
- [ ] Run smoke tests and synthetic checks
- [ ] Validate dashboards and error budgets

## Production Deploy
- [ ] Obtain manual approval via GitHub environment
- [ ] Execute `ci/deploy.yaml` for `production`
- [ ] Monitor for 30 minutes; be ready to rollback

## Rollback
- [ ] Trigger `ci/rollback.yaml` with previous version
- [ ] Confirm recovery signals and post in incident channel

References
- docs/devops/playbooks/README.md
- ci/deploy.yaml
- ci/rollback.yaml

# TODO: Define environment names and approval matrix.