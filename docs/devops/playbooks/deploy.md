### Deploy Playbook

This playbook standardizes safe deployment strategies and progressive delivery.

#### Objectives
- Minimize blast radius with gradual rollouts and fast aborts.
- Ensure consistent environments via IaC and policy controls.

#### Practices
- Use canary/blue-green with health checks and automatic rollback.
  - Source: Google SRE principles on automation and rollbacks: https://sre.google/sre-book/embracing-risk/
- Provision and manage infra as code; review plans.
  - Source: AWS Well-Architected Reliability: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html
- Enforce policies (OPA/Kyverno) and admission controls.

#### Checklist
- Deployment strategy defined (canary/blue-green)
- Health checks, SLO guardrails, and alerts configured
- Rollback tested; feature flag plan ready
- Infra plans reviewed and applied

#### Metrics
- Deployment success rate
- Time-to-detect and time-to-rollback

#### TODOs (org-specific)
- TODO: Link to Kubernetes/infra environments and policies
- TODO: Define standard health endpoints and SLO thresholds