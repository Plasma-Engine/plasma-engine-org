<!--
Explainer: Production release checklist to ensure changes are reviewed,
tested, and safely deployed with clear rollback and verification.
-->

## Release Checklist

### Pre-Release
- [ ] Linked issues closed or approved for release
- [ ] CI green on main (lint, tests, security)
- [ ] Changelog updated and tagged
- [ ] Migration plans validated (DB/IaC)
- [ ] Rollback plan defined and tested

### Release
- [ ] Approvals obtained in GitHub environment
- [ ] Deploy to staging → validate → promote to production
- [ ] Monitor dashboards and logs during rollout

### Post-Release
- [ ] Smoke tests pass in production
- [ ] Error budgets unaffected
- [ ] Announce release notes
- [ ] Update runbooks if needed

### References
- Playbooks: `docs/devops/playbooks/`
- Activity log: `docs/devops/activity-log.md`

