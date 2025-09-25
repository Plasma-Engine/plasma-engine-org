### CI/CD Playbook

Purpose: Define the standard lifecycle for build, test, security, package, deploy, and rollback across services.

Stages:
- Build: compile/package application artifacts
- Test: unit/integration tests, coverage gating
- Security: dependency and image scanning
- Package: container image build and publish to `ghcr.io`
- Deploy: environment-specific rollout with approvals for production
- Rollback: fast revert to last known good release

References:
- GitHub Actions Reusable Workflows: `ci/reusable/*`
- Terraform IaC: `infra/terraform/`

Checklist:
- [ ] Lint and tests pass for all touched components
- [ ] Security scans completed, findings triaged
- [ ] Container image pushed with immutable `sha-<commit>` tag
- [ ] Terraform plan reviewed and approved (if infra changes)
- [ ] Deployment executed to target environment
- [ ] Post-deploy smoke checks green
- [ ] Rollback plan validated and documented

