<!--
Explainer: Security scanning and hardening playbook.
-->

## Scan Steps

- Python: `pip-audit`, `bandit`
- Node: `npm audit --audit-level=high`, `npq` (optional)
- Containers: `trivy image`
- IaC: `tfsec`, `tflint`

# TODO: Define acceptable risk thresholds and exception process.

