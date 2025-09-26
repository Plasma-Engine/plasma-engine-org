### Release Process

This document defines roles, environments, promotion gates, and verification steps for safe, frequent releases.

#### Roles
- Release Manager, Approver(s), QA/SRE, Service Owners

#### Environments & Gates
1) Dev: feature branches/PRs → CI
2) Staging: integration tests, performance checks, security gates
3) Production: manual approval, change window if required

#### Promotion Criteria
- All CI stages green; vulnerability and compliance checks passed
- Staging verification and sign-offs completed
- Rollback plan verified; feature flags mapped

#### Verification & Rollback
- Post-deploy smoke and SLO checks
- Canary analysis; auto-rollback on regression
- Document rollback procedure and success criteria

#### Communications
- Release notes with impact and risks
- Stakeholder notification before and after release

#### References
- DORA/Accelerate: Capabilities for High Performance — https://cloud.google.com/architecture/devops
- AWS Well-Architected Operational Excellence — https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html
- Google SRE Workbook — https://sre.google/workbook/

#### TODOs (org-specific)
- TODO: Add approver matrix and environment protection rules
- TODO: Link to release calendar and change management policy