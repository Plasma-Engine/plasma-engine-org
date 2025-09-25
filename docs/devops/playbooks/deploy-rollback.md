<!--
Explainer: Deploy and rollback playbook. Aligns with CI stages and environment
gates. Update once cloud provider and Helm/K8s details are finalized.
-->

## Deploy
- [ ] Ensure CI stages are green (lint/test/build/security/package)
- [ ] Approve deployment in GitHub environment
- [ ] Apply IaC changes (terraform plan/apply)
- [ ] Roll out application release
- [ ] Monitor metrics and logs

## Rollback
- [ ] Identify last known good version
- [ ] Revert Helm release or redeploy previous artifact
- [ ] Revert IaC state if required
- [ ] Validate recovery (SLOs, smoke tests)

## References
- Runbooks: `docs/devops/runbooks/`
- Release checklist: `docs/devops/release/release-checklist.md`

