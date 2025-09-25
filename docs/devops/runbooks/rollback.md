### Runbook: Rollback Release

Trigger: Deployment causes regression or critical incidents.

Steps:
1. Identify last known good release tag or Terraform state.
2. For app: redeploy previous image tag `sha-<commit>`.
3. For infra: `terraform apply` with prior state or revert module version.
4. Verify recovery: health checks, metrics, error rates.
5. Open incident postmortem ticket.

Checklist:
- [ ] Prior version identified
- [ ] Rollback executed
- [ ] Recovery verified
- [ ] Postmortem created and assigned

