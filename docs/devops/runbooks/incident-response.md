### Incident Response Runbook

This runbook provides a standardized workflow for detecting, triaging, mitigating, and learning from incidents.

#### Prerequisites
- On-call rotation and paging configured
- Access to dashboards, logs, traces, and runbooks
- Communication channels set up (Slack/Email/Status Page)

#### Decision Tree
- Is user impact occurring now? → Page SEV based on impact and SLO breach
- Is the issue mitigatable by rollback/feature flag? → Execute safe rollback
- Is data at risk? → Engage Security/Privacy immediately

#### Standard Operating Procedure
1) Declare the incident and assign roles (Incident Commander, Communications, Ops, SME)
2) Stabilize: rollback, scale, or feature flag to reduce impact
3) Investigate: correlate dashboards and logs; form hypotheses
4) Mitigate: apply fix or workaround; verify recovery and SLOs
5) Communicate: update stakeholders and status page at defined intervals
6) Close: document timeline and actions; schedule postmortem

#### Verification
- User-facing error rates and latency return to within SLOs
- Alerts clear; no ongoing saturation
- Stakeholders confirm resolution; status page updated

#### Postmortem
- Blameless analysis of contributing factors, detection gaps, and remediation items with owners and due dates
- Track follow-ups; review in reliability forum

#### References
- NIST SP 800-61r2: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf
- Google SRE Workbook (Incident Management): https://sre.google/workbook/

#### TODOs (org-specific)
- TODO: Link to severity matrix and paging policy
- TODO: Add status page and stakeholder contact list
- TODO: Add top service runbooks and dashboards