# Rollback Runbook

Purpose: Safely revert to a known-good state for both application and infrastructure.

## Preconditions
- Identify last known-good version and commit/tag
- Ensure access to CI/CD and Terraform state

## Application Rollback
- [ ] Redeploy previous artifact version
- [ ] Verify health checks and error rates
- [ ] Announce rollback completion

## Infrastructure Rollback
- [ ] Review last applied Terraform plan
- [ ] Re-apply previous state as needed
- [ ] Validate networking, IAM, storage states

## Verification
- [ ] Synthetic user journey passes
- [ ] SLOs within thresholds
- [ ] No residual incidents open

References
- ci/rollback.yaml
- docs/devops/runbooks/incident-response.md

# TODO: Add service-specific rollback notes and known good build IDs.