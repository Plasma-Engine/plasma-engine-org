<!--
Explainer: Failed deploy runbook coordinates quick rollback and diagnosis.
-->

## Failed Deploy Runbook

### Immediate Actions
- [ ] Halt rollout and enable maintenance mode if needed
- [ ] Roll back to last known good artifact

### Investigation
- [ ] Compare diffs (config, infra, code)
- [ ] Inspect logs and health checks
- [ ] Validate migrations and feature flags

### Remediation
- [ ] Cherry-pick fix or revert change
- [ ] Re-run CI with targeted tests

### References
- Deploy & rollback playbook: `docs/devops/playbooks/deploy-rollback.md`

