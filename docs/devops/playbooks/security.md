# Playbook: Security Scanning

Purpose: Run dependency and container scans.

Inputs:
- Service path
- Severity threshold

Outputs:
- Vulnerability report artifacts

Commands (examples):
```bash
# Node
yarn audit || npm audit --audit-level=high

# Python
pip-audit

# Containers
trivy fs .
```

TODO: Configure SARIF uploads and PR annotations.