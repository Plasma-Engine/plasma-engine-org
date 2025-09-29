<!--
Explainer: Service outage runbook defines the step-by-step response
for total or near-total loss of service. Use it in conjunction with
monitoring alerts and incident tooling.
-->

## Service Outage Runbook

### Preconditions
- Alert fired from monitoring (PagerDuty/Grafana alert)
- On-call acknowledged

### Objectives
- Restore service quickly and safely
- Minimize customer impact
- Preserve evidence for postmortem

### Triage Checklist
- [ ] Identify blast radius (which regions/services)
- [ ] Check recent deploys/changes
- [ ] Review dashboards: error rate, latency, saturation
- [ ] Correlate logs with request IDs

### Mitigation Actions
- [ ] Roll back to last known good release
- [ ] Scale up impacted components if resource constrained
- [ ] Feature-flag disable suspect paths
- [ ] Apply temporary WAF/IP blocks if under attack

### Communications
- [ ] Update status page and internal channel
- [ ] Assign incident commander and scribe
- [ ] Create tracking issue labeled `incident`

### Validation
- [ ] Verify SLOs recovered
- [ ] Run smoke tests
- [ ] Remove temporary mitigations

### Postmortem
- [ ] Draft timeline and impact
- [ ] Identify contributing factors
- [ ] Create action items with owners and dates

### References
- Observability: `docs/devops/playbooks/observability.md`
- Rollback: `docs/devops/playbooks/deploy-rollback.md`
- DevOps process: `docs/devops-process.md`

