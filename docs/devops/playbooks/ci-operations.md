<!--
Explainer: CI operations playbook that maps to `.github/workflows/ci.yaml`.
-->

## CI Operations

### Stages
- Lint & Format: verify style and formatting
- Tests: run unit/integration tests
- Build: produce artifacts
- Security: dependency and IaC scans
- Package: prepare artifacts for deploy
- Deploy: gated via environments
- Rollback: manual until automation in place

### Common Tasks
- [ ] Re-run failed job with SSH debug if needed
- [ ] Download artifacts from Actions UI for inspection
- [ ] Trigger rollback via workflow_dispatch when necessary

### References
- Workflow: `.github/workflows/ci.yaml`
- Playbooks: deploy-rollback, secrets-management

