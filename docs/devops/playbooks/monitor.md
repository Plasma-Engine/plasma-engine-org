### Monitor Playbook

This playbook standardizes observability, alerting policies, and continuous feedback loops.

#### Objectives
- Detect issues early with actionable alerts; avoid noise.
- Close the loop with learning and improvements.

#### Practices
- Define SLIs and alert on SLO burn rate and user-impacting symptoms.
  - Source: Google SRE SLOs and alerting: https://sre.google/sre-book/monitoring-distributed-systems/
- Adopt the three pillars (logs, metrics, traces) with context propagation.
  - Source: CNCF Observability: https://tag-observability.cncf.io/whitepaper/

#### Checklist
- SLI catalog maintained; SLOs reviewed quarterly
- Alert policies with runbook links and ownership
- On-call friendly thresholds and routing
- Synthetic and real-user monitoring in place

#### Metrics
- Alert signal-to-noise ratio
- MTTR and detection time (MTTD)

#### TODOs (org-specific)
- TODO: Link to monitoring stack and dashboards index
- TODO: Define escalation and paging routing rules