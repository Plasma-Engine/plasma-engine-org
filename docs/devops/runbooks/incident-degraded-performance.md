<!--
Explainer: Degraded performance runbook targets elevated latency, error rate
under thresholds, or partial service impairment.
-->

## Degraded Performance Runbook

### Detection
- [ ] Alerts on latency (p95/p99) or timeouts
- [ ] Throughput drops without traffic changes

### Diagnosis
- [ ] Compare resource saturation (CPU/mem/IO)
- [ ] Check dependency latencies (DB/cache/external)
- [ ] Examine recent deploys and feature flags

### Mitigation
- [ ] Scale out affected components
- [ ] Increase cache TTLs or enable fallback responses
- [ ] Throttle expensive features temporarily

### Validation
- [ ] Monitor SLOs returning to normal
- [ ] Run synthetic probes/smoke tests

### References
- Observability playbook: `docs/devops/playbooks/observability.md`

