<!--
Explainer: Observability playbook covering metrics, logs, tracing, and
alerting standards. Adapt to your actual stack (Grafana/Prometheus,
ELK/OpenSearch, OpenTelemetry collector).
-->

## Observability Playbook

### Signals
- Metrics: RED/USE metrics, service-level metrics
- Logs: JSON with correlation IDs
- Traces: W3C Trace Context, sampled at configurable rate

### Dashboards
- [ ] Service health (latency, error rate, throughput)
- [ ] Dependency health (DB, cache, message bus)
- [ ] Capacity (CPU, memory, disk, I/O)

### Alerts
- [ ] SLO violations (error rate, latency budgets)
- [ ] Saturation (CPU/memory threshold)
- [ ] Anomaly detection on traffic patterns

### Standards
- [ ] Use OpenTelemetry SDKs and collector
- [ ] Enforce JSON logging with request IDs
- [ ] Retention policies documented

### References
- Runbooks: `docs/devops/runbooks/`
- ADR-0002 Platform Tech Stack

> # TODO: Confirm observability vendor and retention SLAs.

