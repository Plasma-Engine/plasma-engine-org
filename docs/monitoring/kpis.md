### Monitoring KPIs and Continuous Improvement

Core KPIs
- Availability (SLO): target 99.9% (per service)
- Error rate: <1% 5xx over 5m window
- Latency (P95): service-specific SLOs
- Cost per request: watch monthly trend
- On-call load: pages per week per engineer

DORA Metrics
- Deployment frequency: goal daily to staging, weekly to prod
- Lead time for changes: PR open → prod deploy < 24h
- Change failure rate: < 15%
- Mean time to restore (MTTR): < 1h

Dashboards & Alerts
- Grafana dashboards per service; golden signals (latency, traffic, errors, saturation)
- Alert thresholds aligned to SLOs with burn-rate alerts

Cadence
- Weekly: KPI and DORA review; open improvements in `docs/backlog/automation.md`
- Monthly: Blameless retrospective, trend analysis, and action pruning

Data Sources
- OpenTelemetry metrics; logs with correlation IDs
- CI metrics (duration, queue time, flake rate)
- Incident logs and postmortems

References
- DevOps Guide: `docs/devops-process.md`
- Exa: exa://plasma-engine/observability-standards

