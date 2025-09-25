# Secrets & Access Management Runbook

Purpose: Manage secrets, keys, and credentials with least privilege and auditability.

## Policies
- Rotate credentials regularly and on incident
- Store secrets in managed vaults; never in git
- Enforce least privilege IAM policies

## Procedures
- [ ] Request access via ticket and approval
- [ ] Provision role/user with time-bound access
- [ ] Store and reference secrets via environment/CI providers

## Rotation
- [ ] Identify affected systems and owners
- [ ] Rotate keys in vault and update consumers
- [ ] Validate and deprecate old credentials

References
- docs/devops/playbooks/README.md
- plasma-engine-infra Terraform IAM/security modules

# TODO: Specify chosen secret manager and key rotation schedule.