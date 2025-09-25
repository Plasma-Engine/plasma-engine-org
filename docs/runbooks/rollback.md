### Runbook: Rollback a Release

Trigger
- Degraded KPIs, incident, or failed smoke tests after deploy.

Steps
1) Halt further deploys (freeze pipeline for the affected service).
2) Identify last known good version (release tag or Helm revision).
3) Roll back application and related infra changes.
4) Verify health checks and KPIs.
5) Record incident and schedule a postmortem.

Commands (examples)
```bash
# If using container tags
git checkout <last-good-tag>
# Re-publish if needed
make build-all && make push-all

# Infra (Terraform plan then apply with approvals)
terraform plan -input=false -no-color | cat
terraform apply -input=false -auto-approve
```

Notes
- Ensure database schema compatibility before rollback; prefer backward-compatible migrations.
- Update `CHANGELOG` with rollback context and follow-up tasks.

References
- DevOps Guide: `docs/devops-process.md`
- Incident Response: `docs/runbooks/incident-response.md`
- Exa: exa://plasma-engine/rollback-patterns

