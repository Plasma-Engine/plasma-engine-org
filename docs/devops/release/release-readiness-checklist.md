### Release Readiness Checklist

This checklist must be satisfied before promoting a release to production.

#### Pre-Release
- CI: lint, tests, build, security scans passed
- SBOM created; artifact signed and stored
- Staging: functional, E2E, and perf checks passed
- Documentation and release notes updated

#### Risk & Compliance
- Security review for high-risk changes
- Data/privacy impact assessed; approvals recorded
- Backup and restore verified within RPO/RTO

#### Deployment
- Rollback plan documented and tested
- Feature flags mapped and default states defined
- Monitoring/alerts in place; runbooks linked

#### Post-Deploy
- Smoke tests and SLO checks defined
- Business and support teams notified

#### References
- DORA capabilities and Four Keys — https://cloud.google.com/devops
- AWS Well-Architected Reliability & Security — https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html

#### TODOs (org-specific)
- TODO: Insert links to specific CI workflows and required checks
- TODO: Add approver names/roles and change window rules