### Operate Playbook

This playbook defines day-2 operations, reliability practices, and error budget policy.

#### Objectives
- Maintain reliability within SLOs; reduce toil via automation.
- Establish clear on-call and incident workflows.

#### Practices
- SLO/error budget policy informs launch pace and risk.
  - Source: Google SRE SLOs and error budgets: https://sre.google/sre-book/service-level-objectives/
- Standardize logging/metrics/traces and dashboards.
  - Source: CNCF Observability whitepaper: https://tag-observability.cncf.io/whitepaper/
- Define on-call rotations, escalation, and postmortems.
  - Source: SRE Workbook: https://sre.google/workbook/

#### Checklist
- On-call schedule and escalation paths defined
- Runbooks for top incidents in place
- Dashboards and alerts reviewed quarterly
- Error budget burn reviewed weekly

#### Metrics
- Alert volume by severity; toil hours
- SLO burn rate and availability

#### TODOs (org-specific)
- TODO: Link to on-call roster and paging policy
- TODO: Add top-N services and ownership map