### Runbook: Deploy Service

Goal: Safely deploy a service to the specified environment.

Pre-Reqs:
- CI artifacts built and published
- Environment credentials configured (OIDC preferred)

Steps:
1. Review CI status and security scan results.
2. Trigger deployment workflow with parameters: service name, environment.
3. Monitor logs and metrics; verify health checks.
4. If issues arise, execute rollback runbook.

References:
- Deployment workflow: `ci/reusable/deploy.yml`
- Observability: `infra/terraform/modules/observability`

Checkboxes:
- [ ] Deployment approved for environment
- [ ] Health checks passed
- [ ] Alerts quiet

