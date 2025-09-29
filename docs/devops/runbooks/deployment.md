# Runbook: Deployment

Audience: Platform and service owners

SLO gates:
- Error rate < 1%
- p95 latency < threshold (TODO: define per service)

Checklist:
- [ ] Release built and tagged
- [ ] Smoke tests defined
- [ ] Dashboards linked

Procedure:
1. Validate release checklist.
2. Deploy to staging and run smoke tests.
3. Monitor KPIs for 30 minutes.
4. Approve production deploy.
5. Post-deploy verification. If failure, follow `rollback.md`.

References:
- Playbook `deploy.md`
- CI workflow `.github/workflows/release.yml`

TODO: Insert dashboard URLs and smoke test commands.