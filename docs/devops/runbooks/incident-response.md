# Runbook: Incident Response

Severity Matrix:
- Sev-1: Full outage or critical data loss
- Sev-2: Partial outage/degradation
- Sev-3: Minor impact

Immediate Actions:
1. Declare incident and assign Incident Commander.
2. Open incident issue and Slack bridge.
3. Mitigation first, diagnosis second.

Triage:
- Gather logs, metrics, traces.
- Roll back risky changes if applicable.
- Engage on-call owners per service.

Communication:
- Post status updates every 15 minutes.
- Publish postmortem within 5 business days.

TODO: Link to paging/rotation policy and dashboards.