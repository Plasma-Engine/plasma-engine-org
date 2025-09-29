# Incident Response Runbook

Purpose: Coordinate fast, consistent response to incidents with clear ownership and rollback paths.

## Prerequisites
- On-call rota and escalation paths
- Access to dashboards, logs, metrics, tracing
- CI permissions for rollback workflows

## Triage Checklist
- [ ] Acknowledge alert in paging system
- [ ] Assign incident commander and scribe
- [ ] Identify blast radius and impacted services
- [ ] Declare severity (SEV-1..SEV-4) and notify stakeholders

## Investigation
- [ ] Correlate logs (JSON + correlation IDs)
- [ ] Inspect metrics (SLOs, error rate, latency, saturation)
- [ ] Trace hot paths with OpenTelemetry

## Mitigation & Rollback
- [ ] Apply feature flags or traffic shaping if available
- [ ] Execute rollback workflow (see `ci/rollback.yaml`)
- [ ] Validate recovery via health checks and dashboards

## Post-Incident
- [ ] Open postmortem issue and link all evidence
- [ ] Capture timeline and contributing factors
- [ ] Define corrective actions with owners and due dates

References
- docs/devops/playbooks/README.md
- docs/devops/runbooks/rollback.md

# TODO: Fill in on-call contacts, paging integration, and escalation matrix.