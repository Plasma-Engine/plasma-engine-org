 # Playbook: Security

 Audience: Security, Platform

 Purpose: Run fast security checks in CI.

 Checklist
 - [ ] Python static analysis (Bandit)
 - [ ] Node dependency audit (npm audit)
 - [ ] Container image scanning (Trivy/Grype) — # TODO integrate

 Workflow Links
 - `.github/workflows/reusable-security.yml`
 - `ci/actions/security/action.yml`

