### On-Call Runbook

This runbook defines expectations, escalation paths, and daily hygiene for on-call engineers.

#### Explainer
On-call engineers safeguard SLOs by responding promptly to actionable alerts and coordinating mitigations per the Incident Response Runbook.

#### Expectations
- Acknowledge pages within target response time (e.g., 5 mins Sev1)
- Use runbooks; avoid risky changes without approval during mitigation
- Provide status updates at defined intervals until resolution/transfer

#### Escalation
- Primary → Secondary → Team Lead → Duty Manager
- Engage SMEs (DB, Networking, Security) per incident context

#### Daily Hygiene
- Review alerts, flakey signals, and dashboards for noise reduction
- Test paging weekly; verify on-call schedule accuracy

#### References
- Google SRE: On-Call and Incident Management — https://sre.google/workbook/

#### TODOs (org-specific)
- TODO: Insert on-call roster link and rotation schedule
- TODO: Add paging tool, contact routes, and override instructions