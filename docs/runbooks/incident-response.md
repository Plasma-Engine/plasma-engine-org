### Runbook: Incident Response

Severity Levels
- SEV-1: Critical outage or major data loss
- SEV-2: Major degradation or partial outage
- SEV-3: Minor degradation or isolated issue

On-call Actions
1) Acknowledge alert and classify severity.
2) Create GitHub Issue labeled `incident` with SEV level and start time.
3) Assign Incident Commander and Scribe.
4) Mitigate impact (scale, rollback, feature flag) using `rollback.md` if needed.
5) Communicate status in the agreed channel; update every 15–30 minutes.
6) Resolve and verify KPIs/health checks return to baseline.
7) Record timeline, root cause, and follow-ups; schedule postmortem within 48 hours.

Commands (examples)
```bash
make logs
make ps

# Triage service-specific logs
kubectl logs deploy/<service> --since=30m | tail -n 200 || true
```

Artifacts
- Incident issue, linked PRs/commits, dashboards, logs, and runbook references.

References
- DevOps Guide: `docs/devops-process.md`
- Runbooks: `rollback.md`, `infra-terraform-apply.md`
- Exa: exa://plasma-engine/incident-handbook

