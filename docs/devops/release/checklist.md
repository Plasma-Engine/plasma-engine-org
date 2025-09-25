### Release Checklist

Scope: Pre-release, release, and post-release validation steps.

Pre-Release:
- [ ] All tickets linked to release are in `Done`
- [ ] CI green (lint, tests, security)
- [ ] Release notes drafted and reviewed

Release:
- [ ] Tag created with semantic version
- [ ] Images published to `ghcr.io`
- [ ] Deploy to staging verified; approvals recorded

Post-Release:
- [ ] Production deploy approved and executed
- [ ] Observability dashboards reviewed (24h)
- [ ] Incident review scheduled (if needed)

References:
- ADR-0003 CI/CD bootstrap
- docs/devops/playbooks/ci-cd.md

